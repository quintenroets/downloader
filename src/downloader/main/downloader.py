import shutil
import time
import urllib.parse
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import TypeVar

import dateutil.parser
import requests
import urllib3
from retry import retry
from superpathlib import Path
from tqdm.utils import CallbackIOWrapper

from .progress import UIProgress

TRIES = 5
CONTENT_MODIFIED = 304
NOT_SATISFIABLE = 416  # range not satisfiable or supported
T = TypeVar("T", int, float)


@dataclass
class Downloader:
    url: str
    target: Path = field(default_factory=Path)
    folder: Path | str = ""
    session: requests.Session = field(default_factory=requests.Session)
    headers: dict[str, str] | None = None
    number_of_retries: int = -1
    timeout: int = 10
    progress_callback: Callable[[float], None] | None = None
    skip_same_size: bool = False
    set_time: bool = True  # set modified time to modified time on server

    def __post_init__(self) -> None:
        self.prepare_destination()
        self.prepare_session()

    def prepare_session(self) -> None:
        browser = (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/85.0.4183.83 Safari/537.36"
        )
        download_time = time.gmtime(self.target.mtime)
        parsed_download_time = time.strftime("%a, %d %b %Y %H:%M:%S GMT", download_time)
        default_headers = {
            "User-Agent": browser,
            "If-Modified-Since": parsed_download_time,
        }
        headers = (self.headers or {}) | default_headers
        self.session.headers.update(headers)

    def prepare_destination(self) -> None:
        target: Path | str
        if self.target.parts:
            target = self.target
        else:
            url_path = urllib.parse.urlparse(self.url).path
            name = urllib.parse.unquote(url_path).split("/")[-1]
            target = name or "download"

        self.target = Path(self.folder) / target if self.folder else Path(target)

    @retry(
        (requests.exceptions.RequestException, urllib3.exceptions.HTTPError),
        tries=TRIES,
    )
    def download(self) -> None:
        self.number_of_retries += 1
        headers = {"Range": f"bytes={self.temporary_target.size}-"}
        if "If-Modified-Since" in self.session.headers:
            self.session.headers.pop("If-Modified-Since")
        stream = self.session.get(
            self.url,
            timeout=self.timeout,
            stream=True,
            headers=headers,
        )
        if stream.status_code != CONTENT_MODIFIED:
            self.download_modified(stream)

    def download_modified(self, stream: requests.Response) -> None:
        if stream.status_code == NOT_SATISFIABLE:
            stream = self.session.get(self.url, timeout=self.timeout, stream=True)
        elif "Content-Range" in stream.headers:
            start = int(
                stream.headers["Content-Range"].split("bytes ")[1].split("-")[0],
            )
            if self.temporary_target.size > start:
                self.temporary_target.unlink()
                stream = self.session.get(self.url, timeout=self.timeout, stream=True)
        elif not stream.ok:
            message = f"Server returned status code {stream.status_code}."
            raise RuntimeError(message)

        skip = self.skip_same_size and self.target.size == int(
            stream.headers["Content-Length"],
        )
        if not skip:
            self.start_download(stream)

    def start_download(self, stream: requests.Response) -> None:
        total = (
            int(
                stream.headers["Content-Length"],
            )  # length that still needs to be received
            if "Content-Length" in stream.headers
            else int(stream.headers["Content-Range"].split("/")[-1])
        )

        progress = UIProgress(self.description, total=total + self.target.size)
        # downloaded size added to todo and done

        def progres_callback(value: float) -> None:
            progress.advance(value)
            if self.progress_callback is not None:
                self.progress_callback(value / total)

        progres_callback(self.target.size)  # already downloaded part is progress

        stream_raw = CallbackIOWrapper(progres_callback, stream.raw)

        chunk_size = self.truncate(total // 10, 1 * 1024, 128 * 1024)
        with progress, self.temporary_target.open("ab") as fp:
            shutil.copyfileobj(stream_raw, fp, length=chunk_size)

        self.temporary_target.rename(self.target)
        modified_key = "last-modified"
        if self.set_time and modified_key in stream.headers:
            server_mtime = stream.headers[modified_key]
            self.target.mtime = dateutil.parser.parse(server_mtime).timestamp()

    @property
    def temporary_target(self) -> Path:
        return self.target.with_suffix(self.target.suffix + ".part")

    @property
    def description(self) -> str:
        return (
            f"[retry {self.number_of_retries}/{TRIES - 1}] {self.target.name}"
            if self.number_of_retries > 0
            else self.target.name
        )

    @staticmethod
    def truncate(value: T, min_value: T, max_value: T) -> T:
        if value < min_value:
            value = min_value
        elif value > max_value:
            value = max_value
        return value

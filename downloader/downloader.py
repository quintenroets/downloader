import shutil
import time
import urllib.parse

import requests
import rich.progress as progress
import urllib3
from retry import retry
from tqdm.utils import CallbackIOWrapper

from plib import Path

from .progress import UIProgress

TRIES = 5


class Downloader:
    def __init__(
        self,
        url,
        dest=None,
        folder=None,
        session=None,
        headers=None,
        progress_callback=None,
        timeout=10,
        skip_same_size=False,
    ):
        self.url = url
        self.dest = self.prepare_dest(dest, folder)
        self.session = self.prepare_session(session, headers)

        self.retry = -1
        self.timeout = timeout
        self.progress_callback = progress_callback or (lambda p: None)
        self.skip_same_size = skip_same_size

    def prepare_session(self, session, headers):
        session = session or requests.Session()
        browser = (
            "Mozilla/5.0 (X11; Linux x86_64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/85.0.4183.83 Safari/537.36"
        )
        download_time = time.gmtime(self.dest.mtime)
        download_time = time.strftime("%a, %d %b %Y %H:%M:%S GMT", download_time)
        headers = (headers or {}) | {
            "User-Agent": browser,
            "If-Modified-Since": download_time,
        }
        session.headers.update(headers)
        return session

    def prepare_dest(self, dest, folder):
        if dest is None:
            url_path = urllib.parse.urlparse(self.url).path
            name = urllib.parse.unquote(url_path).split("/")[-1]
            dest = name or "download"

        dest = Path(folder) / dest if folder else Path(dest)
        return dest

    @retry(
        (requests.exceptions.RequestException, urllib3.exceptions.HTTPError),
        tries=TRIES,
    )
    def download(self):
        self.retry += 1
        headers = {"Range": f"bytes={self.temp_dest.size}-"}
        if "If-Modified-Since" in self.session.headers:
            self.session.headers.pop("If-Modified-Since")
        stream = self.session.get(
            self.url, timeout=self.timeout, stream=True, headers=headers
        )
        if stream.status_code != 304:
            self.download_modified(stream)

    def download_modified(self, stream):
        if stream.status_code == 416:  # range not satifiable or supported
            stream = self.session.get(self.url, timeout=self.timeout, stream=True)
        elif "Content-Range" in stream.headers:
            start = int(
                stream.headers["Content-Range"].split("bytes ")[1].split("-")[0]
            )
            if self.temp_dest.size > start:
                self.temp_dest.unlink()
                stream = self.session.get(self.url, timeout=self.timeout, stream=True)
        else:
            assert stream.ok

        skip = self.skip_same_size and self.dest.size == int(
            stream.headers["Content-Length"]
        )
        if not skip:
            self.start_download(stream)

    def start_download(self, stream):
        if "Content-Length" in stream.headers:
            total = int(
                stream.headers["Content-Length"]
            )  # length that still needs to be received
        else:
            total = int(stream.headers["Content-Range"].split("/")[-1])
        progress = UIProgress(self.description, total=total)

        def progres_callback(value):
            progress.advance(value)
            self.progress_callback(value / total)

        stream_raw = CallbackIOWrapper(progres_callback, stream.raw)

        chunk_size = self.truncate(total // 10, 1 * 1024, 128 * 1024)
        with progress, self.temp_dest.open("ab") as fp:
            shutil.copyfileobj(stream_raw, fp, length=chunk_size)

        self.temp_dest.rename(self.dest)

    @property
    def temp_dest(self):
        return self.dest.with_suffix(self.dest.suffix + ".part")

    @property
    def description(self):
        desc = (
            f"[retry {self.retry}/{TRIES - 1}] {self.dest.name}"
            if self.retry > 0
            else self.dest.name
        )
        return desc

    @staticmethod
    def truncate(value, min_value, max_value):
        if value < min_value:
            value = min_value
        elif value > max_value:
            value = max_value
        return value

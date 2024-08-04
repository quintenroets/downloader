import threading
from collections.abc import Iterable
from typing import Any

from superpathlib import Path

from .downloader import Downloader


def download(url: str, target: Path | None = None, **kwargs: Any) -> Path:
    if target is None:
        target = Path()
    downloader = Downloader(url, target=target, **kwargs)
    downloader.download()
    return downloader.target


def get(*urls: Any, **kwargs: Any) -> list[bytes]:
    """Get the content of urls and cache it to a local file.

    Useful to speed up the process when the same url is requested
    multiple times
    """
    folder = Path.HOME / ".cache" / "downloader"
    urls_mapping = {u: folder / "_".join(u.split("/")) for u in urls}
    dest_paths = download_urls(urls_mapping, **kwargs)
    return [dest_path.byte_content for dest_path in dest_paths]


def download_urls(
    urls: dict[str, Path | str] | Iterable[str],
    **kwargs: Any,
) -> list[Path]:
    downloaders = (
        [Downloader(url, Path(target), **kwargs) for url, target in urls.items()]
        if isinstance(urls, dict)
        else [Downloader(url, **kwargs) for url in urls]
    )
    threads = [threading.Thread(target=d.download) for d in downloaders]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return [downloader.target for downloader in downloaders]

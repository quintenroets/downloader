import threading

from superpathlib import Path

from .downloader import Downloader


def download(url: str, dest: Path | None = None, **kwargs):
    downloader = Downloader(url, dest=dest, **kwargs)
    downloader.download()
    return downloader.dest


def get(*urls, **kwargs):
    """Get the content of urls and cache it to a local file.

    Useful to speed up the process when the same url is requested
    multiple times
    """
    folder = Path.HOME / ".cache" / "downloader"
    urls = {u: folder / "_".join(u.split("/")) for u in urls}
    dest_paths = download_urls(urls, **kwargs)
    return [dest_path.byte_content for dest_path in dest_paths]


def download_urls(urls, **kwargs):
    downloaders = (
        [Downloader(url, dest, **kwargs) for url, dest in urls.items()]
        if isinstance(urls, dict)
        else [Downloader(url, **kwargs) for url in urls]
    )
    threads = [threading.Thread(target=d.download) for d in downloaders]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return [d.dest for d in downloaders]

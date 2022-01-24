import threading

from plib import Path

from .downloader import Downloader


def get(*urls, **kwargs):
    """
    Get the content of urls and cache it to a local file.
    Useful to speed up the process when the same url is requested multiple times
    """
    folder = Path.HOME / ".cache" / "downloader"
    urls = {u: folder / "_".join(u.split("/")) for u in urls}
    dests = download_urls(urls, **kwargs)
    return [d.byte_content for d in dests]


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


def download(url, dest=None, **kwargs):
    d = Downloader(url, dest=dest, **kwargs)
    d.download()
    return d.dest

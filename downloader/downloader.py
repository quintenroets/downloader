import requests
import shutil
import threading
import time
import urllib.parse

from plib import Path
from tqdm import tqdm
from tqdm.utils import CallbackIOWrapper


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
    downloaders = [
        Downloader(url, dest, **kwargs) for url, dest in urls.items()
    ] if isinstance(urls, dict) else [
        Downloader(url, **kwargs) for url in urls
    ]
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


class Downloader:
    def __init__(self, url, dest=None, folder=None, session=None, headers=None, progress_callback=None, retries=4, timeout=10,
                 overwrite_identical_size=True
                 ):
        self.url = url
        dest = dest or Downloader.url_name(url) or "download"
        if folder:
            dest = Path(folder) / dest
        self.dest = Path(dest)
        
        self.session = session or requests.Session()
        self.session.stream = True
        
        user_agent = (
            'Mozilla/5.0 (X11; Linux x86_64) '
            'AppleWebKit/537.36 (KHTML, like Gecko) '
            'Chrome/85.0.4183.83 Safari/537.36'
        )
        check_time = time.strftime('%a, %d %b %Y %H:%M:%S GMT', time.gmtime(self.dest.mtime))
        
        headers = headers or {}
        headers['User-Agent'] = user_agent  # browser user agent often required
        headers['If-Modified-Since'] = check_time
        self.session.headers.update(headers)
        self.not_modified = False
        
        self.retries = retries
        self.retry = 0
        self.timeout = timeout
        self.progress_callback = progress_callback or (lambda p: None)
        self.overwrite_identical_size = overwrite_identical_size
        
    @staticmethod
    def url_name(url):
        url_path = urllib.parse.urlparse(url).path
        name = urllib.parse.unquote(url_path).split("/")[-1]
        return name
        
    @property
    def temp_dest(self):
        return self.dest.with_suffix(self.dest.suffix + ".part")
    
    def download(self):
        succes = False
        
        while not succes and self.retry <= self.retries:
            try:
                self.try_download()
            except requests.exceptions.RequestException:
                self.retry += 1
            else:
                succes = True
                    
        if succes:
            if not self.not_modified:
                self.temp_dest.rename(self.dest)
        else:
            raise requests.exceptions.RequestException
        
    def try_download(self):
        self.session.headers["Range"] = f"bytes={self.temp_dest.size}-"
        stream = self.session.get(self.url, timeout=self.timeout)
        
        if stream.status_code == 304:
            self.not_modified = True
        elif stream.status_code == 416: # range not satifiable or supported
            self.session.headers.pop("Range")
            stream = self.session.get(self.url, timeout=self.timeout)
            start = 0
        elif 'Content-Range' in stream.headers:
            start = int(stream.headers["Content-Range"].split("bytes ")[1].split("-")[0])
        elif stream.ok:
            start = 0
        else:
            raise requests.exceptions.RequestException
        
        if not self.not_modified:
            self.not_modified = not self.overwrite_identical_size and self.dest.size == int(stream.headers["Content-Length"])
        
        if not self.not_modified:
            self.start_download(start, stream)
            
    def start_download(self, start, stream):
        if self.temp_dest.size > start:
            self.temp_dest.unlink()
            start = 0
        
        total = int(stream.headers["Content-Length"])  # length that still needs to be received        
        chunk_size = min(total // 10, 128 * 1024)  # max 128 KB
        chunk_size = max(chunk_size, 1)  # min 1 KB
        desc = f"Downloading {self.dest.name}"
        if self.retry > 0:
            desc += f" (retry {self.retry}/{self.retries}"
                        
        with tqdm(total=total, desc=desc, unit="B", unit_scale=True, unit_divisor=1024) as progress:
            def callback(value):
                progress.update(value)
                self.progress_callback(value / progress.total)
                
            stream_raw = CallbackIOWrapper(callback, stream.raw)
            with self.temp_dest.open("ab") as fp:
                shutil.copyfileobj(stream_raw, fp, length=chunk_size)

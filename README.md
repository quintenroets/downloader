# Downloader
[![PyPI version](https://badge.fury.io/py/fire-downloader.svg)](https://badge.fury.io/py/fire-downloader)
![PyPI downloads](https://img.shields.io/pypi/dm/fire-downloader)
![Python version](https://img.shields.io/badge/python-3.10+-brightgreen)
![Operating system](https://img.shields.io/badge/os-linux%20%7c%20macOS-brightgreen)
![Coverage](https://img.shields.io/badge/coverage-91%25-brightgreen)

Download urls in a script as if you would download them from your browser

Features:
* Downloads multiple urls in parallel
* Downloads in chunks
* Automatically retries and continues from partial downloads after error
* Saves downloads and skips re-downloading the same url unless the server indicates an update
* Shows progressbar during download
* Supports custom callback on progress updates

Optional options:
* Destination location
* Number of retries
* Headers, session or cookies for download request
* Whether to overwrite the download if the newly downloaded file has the same size

## Usage
### Cli

```shell
download url
```

### Python scripts

```python
import downloader
```

* Download single url:

```python
downloader.download(url)
```

* Download multiple urls:

```python
downloader.download_urls(url)
```

## Installation
```shell
pip install fire-downloader
```

# Downloader

Download urls in a script as if you would download them from your browser

Features:
* Only downloads when the destination does not exist yet or when the server indicates that there is a newer version
* Automatically retry after error
* Continue from partial download after error
* Show progressbar during download
* Download multiple urls in parallel
* Specify custom callback on progress update

Optional options:
* Destination location
* Number of retries
* Headers, session or cookies for download request
* Whether to overwrite the download if the newly downloaded file has the same size

## Installation

```shell
pip install git+https://github.com/quintenroets/downloader
```

## Usage

### Cli

```shell
download url
```

### Python scripts

```shell
import downloader
```

* Download single url:

```shell
downloader.download(url)
```

* Download multiple urls:

```shell
downloader.download_urls(url)
```

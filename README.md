# Downloader

Download urls in a script as if you would download them from your browser

Features:
* Only downloads the destination does not exist or the server indicates that there is a newer version
* Automatically retry after error
* Continue from partial download after error
* Show progressbar during download
* Download multiple urls in separate threads
* Specify custom callback on progress update

Options to specify:
* Destination location
* Number of retries
* Headers, session or cookies for download request
* Whether to overwrite the download if the newly downloaded file has the same size

Script to visualize the current pandemic situation in Belgium.

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

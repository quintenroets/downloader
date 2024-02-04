import downloader


def test_download(download_url: str) -> None:
    dest = downloader.download(download_url)
    dest.unlink()


def test_multiple_downloads(download_url: str) -> None:
    urls = [
        "https://covid-19.sciensano.be/sites/default/files/Covid19/Meest%20recente%20update.pdf",
        download_url,
    ]

    dest_paths = downloader.download_urls(urls)
    for path in dest_paths:
        path.unlink()

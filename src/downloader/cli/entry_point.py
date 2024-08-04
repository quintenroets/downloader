from typing import Annotated

import typer
from package_utils.cli import create_entry_point
from superpathlib import Path

import downloader


def download(
    url: Annotated[str, typer.Argument(help="The url to download")],
    dest: Annotated[
        Path | None,
        typer.Option(help="The local file to save the download"),
    ] = None,
) -> Path:
    """
    Download url to file with option to retry on errors and resume from partial
    downloads.
    """
    return downloader.download(url, dest)


entry_point = create_entry_point(download)

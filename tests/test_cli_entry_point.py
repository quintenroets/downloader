from downloader import cli
from package_dev_utils.tests.args import cli_args
from plib import Path


def test_entry_point(download_url: str) -> None:
    with Path.tempfile() as path:
        with cli_args(download_url, "--dest", path):
            cli.entry_point()

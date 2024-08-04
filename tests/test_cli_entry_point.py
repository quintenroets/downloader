from downloader import cli
from package_dev_utils.tests.args import cli_args
from superpathlib import Path


def test_entry_point(download_url: str) -> None:
    path = Path.tempfile()
    args = cli_args(download_url, "--dest", path)
    with path, args:
        cli.entry_point()

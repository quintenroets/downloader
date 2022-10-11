import argparse

import downloader


def main():
    parser = argparse.ArgumentParser(
        description="Download url to file with option to retry on errors and resume from partial downloads"
    )
    parser.add_argument("url", help="The url to download")
    parser.add_argument(
        "dest", nargs="?", help="The local file to save the download", default=None
    )
    args = parser.parse_args()

    downloader.download(args.url, args.dest)


if __name__ == "__main__":
    main()

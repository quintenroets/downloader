from collections.abc import Iterator

import pytest


@pytest.fixture(scope="session")
def download_url() -> Iterator[str]:
    yield "https://www.orimi.com/pdf-test.pdf"

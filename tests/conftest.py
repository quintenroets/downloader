import pytest


@pytest.fixture(scope="session")
def download_url() -> str:
    return "https://www.orimi.com/pdf-test.pdf"

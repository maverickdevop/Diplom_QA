import pytest
from config import API_KEY


@pytest.fixture(scope="function")
def headers_get():
    return {
        "Content-Type": "application/json",
        "x-api-key": API_KEY,
    }


@pytest.fixture(scope="function")
def headers_post():
    return {
        "x-api-key": API_KEY
    }

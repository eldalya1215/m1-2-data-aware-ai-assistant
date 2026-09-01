import os

os.environ["STORAGE_BACKEND"] = "memory"
os.environ["AI_BACKEND"] = "mock"

import pytest
from fastapi.testclient import TestClient

from app.dependencies import get_repository
from app.main import app


@pytest.fixture(autouse=True)
def reset_repository():
    get_repository.cache_clear()
    yield
    get_repository.cache_clear()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client

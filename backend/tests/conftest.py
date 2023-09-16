import pytest
from litestar.testing import TestClient

from app.main import app


@pytest.fixture
def test_client() -> TestClient:
    return TestClient(app)

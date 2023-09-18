from typing import TYPE_CHECKING
from urllib.parse import quote_plus

import pytest
from litestar.testing import TestClient
from models.user import PublicUserModel

if TYPE_CHECKING:
    from tests.conftest import AccountDetails


def test_account_public(account: "AccountDetails", test_client: TestClient) -> None:
    resp = test_client.get(f"/controllers/account/{quote_plus(account.email)}/public")

    assert resp.status_code == 200

    resp_json = resp.json()

    try:
        PublicUserModel(**resp_json)
    except:
        assert False, "Given data doesn't match PublicUserModel"

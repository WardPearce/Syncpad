import base64
import time
from secrets import token_urlsafe
from typing import Iterator
from urllib.parse import quote_plus

import pytest
from bson import ObjectId
from litestar.testing import TestClient
from nacl.signing import SigningKey
from pydantic import BaseModel, ValidationError

from app.main import app
from app.models.jwt import UserJtiModel
from app.models.user import UserModel, UserToSignModel


@pytest.fixture(scope="session")
def test_client() -> Iterator[TestClient]:
    with TestClient(app=app) as test_client:
        yield test_client


class AccountDetails(BaseModel):
    csrftoken: str
    token: str
    email: str


@pytest.fixture(scope="session")
def account(test_client: TestClient) -> Iterator[AccountDetails]:
    signing_key = SigningKey.generate()
    email = f"{token_urlsafe()}@example.com".lower()

    resp = test_client.get(f"/controllers/account/{email}/public")

    assert resp.status_code == 404

    csrf_token = resp.cookies["csrftoken"]

    resp = test_client.post(
        "/controllers/account/create",
        json={
            "auth": {
                "public_key": base64.b64encode(signing_key.verify_key.encode()).decode()
            },
            "keypair": {
                "iv": "string",
                "public_key": "string",
                "cipher_text": "string",
            },
            "sign_keypair": {
                "iv": "string",
                "public_key": "string",
                "cipher_text": "string",
            },
            "keychain": {"iv": "string", "cipher_text": "string"},
            "kdf": {
                "salt": "string",
                "time_cost": 2,
                "memory_cost": 65535,
            },
            "signature": "string",
            "email": email,
            "ip_lookup_consent": True,
            "algorithms": "string",
        },
        headers={"x-csrftoken": csrf_token},
    )

    assert (
        resp.status_code == 201
    ), f"Account creation responded with {resp.status_code}"

    resp = test_client.get(f"/controllers/account/{quote_plus(email)}/to-sign")

    assert resp.status_code == 200

    given_code = resp.json()

    try:
        UserToSignModel(to_sign=given_code["to_sign"], _id=ObjectId(given_code["id"]))
    except ValidationError:
        assert False, "Response doesn't match UserToSignModel"

    signed = signing_key.sign(given_code["to_sign"].encode())

    resp = test_client.post(
        f"/controllers/account/{email}/login",
        json={
            "signature": base64.b64encode(signed).decode(),
            "_id": given_code["id"],
            "one_day_login": False,
        },
        headers={"x-csrftoken": csrf_token},
    )

    assert resp.status_code == 201

    resp_json = resp.json()

    resp_json["user"]["_id"] = ObjectId(resp_json["user"]["id"])

    try:
        UserJtiModel(
            jti=ObjectId(resp_json["jti"]), user=UserModel(**resp_json["user"])
        )
    except ValidationError:
        assert False, "Response doesn't match UserJtiModel"

    yield AccountDetails(csrftoken=csrf_token, token=resp.cookies["token"], email=email)

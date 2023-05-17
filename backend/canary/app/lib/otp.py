from datetime import datetime, timedelta, timezone
from hashlib import sha256
from typing import TYPE_CHECKING, Optional

import pyotp
from app.errors import InvalidAccountAuth
from app.models.user import UserModel
from bson import ObjectId

if TYPE_CHECKING:
    from app.types import State


class OneTimePassword:
    def __init__(self, state: "State", key: str) -> None:
        self.__hotp = pyotp.TOTP(key, digits=6)
        self.get_provisioning_uri = self.__hotp.provisioning_uri
        self.verify = self.__hotp.verify
        self.state = state

    @classmethod
    def create(cls, state: "State") -> "OneTimePassword":
        return OneTimePassword(state=state, key=pyotp.random_base32())

    @classmethod
    async def validate_user(
        cls, state: "State", model: UserModel, given_code: Optional[str]
    ) -> None:
        if given_code is None:
            raise InvalidAccountAuth()

        otp_search = {
            "otp_code": given_code,
            "owner_id": ObjectId(model.id),
        }

        otp_count = await state.mongo.old_otp.count_documents(otp_search)
        if otp_count > 0:
            raise InvalidAccountAuth()

        if not OneTimePassword(state=state, key=model.otp.secret).verify(given_code):
            raise InvalidAccountAuth()

        await state.mongo.old_otp.insert_one(
            {
                **otp_search,
                "expires": datetime.now(tz=timezone.utc) + timedelta(seconds=60),
            }
        )

from datetime import datetime, timedelta
from hashlib import sha256
from typing import TYPE_CHECKING, Optional

import pyotp
from bson import ObjectId

from app.errors import InvalidAccountAuth
from app.models.user import UserModel

if TYPE_CHECKING:
    from app.custom_types import State


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
            "user_id": ObjectId(model.id),
        }

        otp_count = await state.mongo.old_otp.count_documents(otp_search)
        if otp_count > 0:
            raise InvalidAccountAuth()

        if model.otp.secret is None:
            raise InvalidAccountAuth()

        if not OneTimePassword(state=state, key=model.otp.secret).verify(given_code):
            raise InvalidAccountAuth()

        await state.mongo.old_otp.insert_one(
            {
                **otp_search,
                "expires": datetime.utcnow() + timedelta(seconds=60),
            }
        )

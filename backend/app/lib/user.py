import secrets
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Union

from bson import ObjectId

from app.errors import UserNotFoundException
from app.models.user import UserModel

if TYPE_CHECKING:
    from app.custom_types import State


async def generate_email_validation(state: "State", email: str) -> str:
    """Generate email validation code.

    Args:
        state (State)
        email (str)

    Returns:
        str: Validation code
    """

    email_secret = secrets.token_urlsafe(32)

    await state.mongo.email_verification.insert_one(
        {
            "secret": email_secret,
            "email": email,
            "expires": datetime.utcnow() + timedelta(hours=24),
        }
    )

    return email_secret


class User:
    def __init__(self, state: "State", identifier: Union[str, ObjectId]) -> None:
        self.state = state
        self.__identifier = identifier
        self.__is_str = isinstance(identifier, str)

    @property
    def _user_query(self) -> dict:
        return (
            {"email": self.__identifier}
            if self.__is_str
            else {"_id": self.__identifier}
        )

    async def exists(self) -> None:
        """Check if user exists.

        Raises:
            UserNotFoundException
        """

        if await self.state.mongo.user.count_documents(self._user_query) == 0:
            raise UserNotFoundException()

    async def get(self, redact_otp: bool = False) -> UserModel:
        """Get user account details.

        Args:
            redact_otp (bool, optional): Redact OTP secret. Defaults to False.

        Raises:
            UserNotFoundException

        Returns:
            UserModel
        """

        user = await self.state.mongo.user.find_one(self._user_query)
        if not user:
            raise UserNotFoundException()

        if not redact_otp:
            return UserModel(**user)
        else:
            user["otp"]["secret"] = None
            return UserModel(**user)

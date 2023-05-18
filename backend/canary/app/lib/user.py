from typing import TYPE_CHECKING, Union

import pyotp
from app.errors import UserNotFoundException
from app.models.user import UserModel
from bson import ObjectId
from env import SETTINGS

if TYPE_CHECKING:
    from app.types import State


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

    async def get(self) -> UserModel:
        """Get user account details.

        Raises:
            UserNotFoundException

        Returns:
            UserModel
        """

        user = await self.state.mongo.user.find_one(self._user_query)
        if not user:
            raise UserNotFoundException()

        return UserModel(**user)

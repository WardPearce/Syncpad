from typing import TYPE_CHECKING

import aiodns
import yarl
from app.env import SETTINGS
from app.errors import CanaryNotFoundException, DomainValidationError
from app.models.canary import CanaryModel
from bson import ObjectId

if TYPE_CHECKING:
    from app.types import State


class CanaryUser:
    def __init__(self, upper: "Canary", user_id: ObjectId) -> None:
        self.__upper = upper
        self.__user_id = user_id

    @property
    def _canary_query(self) -> dict:
        return {"domain": self.__upper._domain, "user_id": self.__user_id}

    async def get(self) -> CanaryModel:
        result = await self.__upper._state.mongo.canary.find_one(self._canary_query)
        if not result:
            raise CanaryNotFoundException()

        return CanaryModel(**result)

    async def attempt_verify(self) -> None:
        """Attempt to verify a canary domain.

        Args:
            state (State)
            user_id (ObjectId)

        Raises:
            DomainValidationError
        """

        if not self.__upper._domain:
            raise DomainValidationError()

        resolver = aiodns.DNSResolver(timeout=SETTINGS.canary.domain_verify.timeout)

        try:
            txt_records = await resolver.query(self.__upper._domain, "TXT")
        except aiodns.error.DNSError:
            raise DomainValidationError()

        canary_code = ""
        for attempts, record in enumerate(txt_records):
            if attempts > 100:
                break

            if record.text.startswith(SETTINGS.canary.domain_verify.prefix):
                canary_code = record.text.replace(
                    SETTINGS.canary.domain_verify.prefix, "", 1
                )
                break

        canary_code = canary_code.strip()

        if not canary_code:
            raise DomainValidationError()

        canary_search = {"user_id": self.__user_id, "verify.code": canary_code}
        if await self.__upper._state.mongo.canary.count_documents(canary_search) == 0:
            raise DomainValidationError()

        await self.__upper._state.mongo.canary.update_one(
            canary_search, {"$set": {"verify.completed": True}}
        )


class Canary:
    def __init__(self, state: "State", domain: str) -> None:
        _domain = yarl.URL(domain).host
        if not _domain:
            self._domain = domain
        else:
            self._domain = _domain

        self._state = state

    def user(self, user_id: ObjectId) -> CanaryUser:
        return CanaryUser(self, user_id)

import hashlib
import json
from datetime import datetime
from typing import TYPE_CHECKING

import yarl
from app.env import SETTINGS
from app.errors import CanaryNotFoundException, DomainValidationError
from app.models.canary import CanaryModel, PublicCanaryModel
from bson import ObjectId

if TYPE_CHECKING:
    from custom_types import State


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

    async def delete(self) -> None:
        """Delete a canary"""

        canary = await self.get()
        if canary.domain_verification.completed:
            # Block canary from ever being recreated with that domain.
            await self.__upper._state.mongo.deleted_canary.insert_one(
                {
                    "domain_hash": hashlib.sha256(
                        self.__upper._domain.encode()
                    ).hexdigest(),
                    "deleted": datetime.utcnow(),
                }
            )

        await self.__upper._state.mongo.canary_warrant.delete_many(
            {"canary_id": canary.id}
        )

        await self.__upper._state.mongo.canary.delete_one(self._canary_query)

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

        resp = await self.__upper._state.aiohttp.get(
            f"https://cloudflare-dns.com/dns-query?name={self.__upper._domain}&type=TXT",
            headers={"accept": "application/dns-json"},
        )
        if resp.status != 200:
            raise DomainValidationError()

        # Aiolibs multi dict doesn't phase correctly, can't use resp.json().
        resp_json = json.loads(await resp.text())

        # Ensure no errors.
        if resp_json["Status"] != 0:
            raise DomainValidationError()

        # Require DNSSEC validation.
        if resp_json["CD"]:
            raise DomainValidationError()

        if "Answer" not in resp_json:
            raise DomainValidationError()

        txt_records = resp_json["Answer"]

        canary_code = ""
        for attempts, record in enumerate(txt_records):
            if attempts > 100:
                break

            striped_data = record["data"].strip('"')

            if striped_data.startswith(SETTINGS.canary.domain_verify.prefix):
                canary_code = striped_data.replace(
                    SETTINGS.canary.domain_verify.prefix, "", 1
                )
                break

        canary_code = canary_code.strip()

        if not canary_code:
            raise DomainValidationError()

        canary_search = {
            "user_id": self.__user_id,
            "domain_verification.code": canary_code,
        }
        if await self.__upper._state.mongo.canary.count_documents(canary_search) == 0:
            raise DomainValidationError()

        await self.__upper._state.mongo.canary.update_one(
            canary_search, {"$set": {"domain_verification.completed": True}}
        )

        # Delete any canaries of the same domain awaiting approval.
        await self.__upper._state.mongo.canary.delete_many(
            {"domain": self.__upper._domain, "domain_verification.completed": False}
        )


class Canary:
    def __init__(self, state: "State", domain: str) -> None:
        _domain = yarl.URL(domain).host
        if not _domain:
            self._domain = domain
        else:
            self._domain = _domain

        self._state = state

    @property
    def __canary_where(self) -> dict:
        return {"domain": self._domain, "domain_verification.completed": True}

    async def exists(self) -> None:
        if self._state.mongo.canary.count_documents(self.__canary_where) == 0:
            raise CanaryNotFoundException()

    async def get(self) -> PublicCanaryModel:
        result = await self._state.mongo.canary.find_one(self.__canary_where)
        if not result:
            raise CanaryNotFoundException()

        return PublicCanaryModel(**result)

    def user(self, user_id: ObjectId) -> CanaryUser:
        return CanaryUser(self, user_id)

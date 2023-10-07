import asyncio
import hashlib
import json
from datetime import datetime
from typing import TYPE_CHECKING
from urllib.parse import quote_plus

import yarl
from bson import ObjectId
from lib.ntfy import push_notification
from lib.smtp import send_email
from lib.url import untrusted_http_request
from lib.user import User
from models.user import NotificationEnum

from app.env import SETTINGS
from app.errors import CanaryNotFoundException, DomainValidationError
from app.models.canary import CanaryModel, PublicCanaryModel

if TYPE_CHECKING:
    from app.custom_types import State


class CanaryUser:
    def __init__(self, upper: "Canary", user_id: ObjectId) -> None:
        self.__upper = upper
        self.__user_id = user_id

    @property
    def _canary_query(self) -> dict:
        if not self.__upper._object_id:
            return {"domain": self.__upper.identifier, "user_id": self.__user_id}
        else:
            return {"_id": self.__upper.identifier, "user_id": self.__user_id}

    async def get(self) -> CanaryModel:
        result = await self.__upper._state.mongo.canary.find_one(self._canary_query)
        if not result:
            raise CanaryNotFoundException()

        return CanaryModel(**result)

    async def delete(self) -> None:
        """Delete a canary"""

        canary = await self.get()

        deleted = await self.__upper._state.mongo.canary.delete_one(self._canary_query)

        if deleted.deleted_count > 0:
            if canary.domain_verification.completed:
                # Block canary from ever being recreated with that domain.
                await self.__upper._state.mongo.deleted_canary.insert_one(
                    {
                        "domain_hash": hashlib.sha256(
                            canary.domain.encode()
                        ).hexdigest(),
                        "deleted": datetime.utcnow(),
                    }
                )

            await self.__upper._state.mongo.canary_warrant.delete_many(
                {"canary_id": canary.id}
            )

    async def attempt_verify(self) -> None:
        """Attempt to verify a canary domain.

        Args:
            state (State)
            user_id (ObjectId)

        Raises:
            DomainValidationError
        """

        if not self.__upper.identifier:
            raise DomainValidationError()

        resp = await self.__upper._state.aiohttp.get(
            f"https://cloudflare-dns.com/dns-query?name={quote_plus(self.__upper.identifier)}&type=TXT",
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
            {"domain": self.__upper.identifier, "domain_verification.completed": False}
        )


class Canary:
    def __init__(self, state: "State", identifier: str | ObjectId) -> None:
        if not isinstance(identifier, ObjectId):
            self._object_id = False
            _identifier: str | None = yarl.URL(identifier).host
            if not _identifier:
                self.identifier = identifier
            else:
                self.identifier = _identifier
        else:
            self._object_id = True
            self.identifier = identifier

        self._state = state

    @property
    def __canary_where(self) -> dict:
        if not self._object_id:
            return {"domain": self.identifier, "domain_verification.completed": True}
        else:
            return {"_id": self.identifier, "domain_verification.completed": True}

    async def exists(self) -> None:
        if self._state.mongo.canary.count_documents(self.__canary_where) == 0:
            raise CanaryNotFoundException()

    async def get(self) -> PublicCanaryModel:
        result = await self._state.mongo.canary.find_one(self.__canary_where)
        if not result:
            raise CanaryNotFoundException()

        return PublicCanaryModel(**result)

    async def alert_subscribers(self, warrant: dict) -> None:
        canary = await self.get()

        futures = []

        subject = f"A new canary warrant has been published for {canary.domain}"
        message = f"Please visit the canary for {canary.domain} to view the latest statement.\n\nNever trust any claims made via emails about canaries."

        async for subscribed in self._state.mongo.subscribed_canary.find(
            {"canary_id": canary.id}
        ):
            user = await User(self._state, subscribed["user_id"]).get()

            if any(
                NotificationEnum.canary_subscriptions.value == enum.value
                for enum in user.notifications.email
            ):
                futures.append(
                    send_email(
                        user.email,
                        subject,
                        message,
                    )
                )

            if any(
                NotificationEnum.canary_subscriptions.value == enum.value
                for enum in user.notifications.push
            ):
                futures.append(
                    push_notification(
                        self._state,
                        topic=user.notifications.push[
                            NotificationEnum.canary_subscriptions
                        ],
                        message=message,
                        title=subject,
                        tags="mailbox_with_mail",
                        priority="high",
                    )
                )

            if any(
                NotificationEnum.canary_subscriptions.value == enum.value
                for enum in user.notifications.webhooks
            ):
                for webhook in user.notifications.webhooks[
                    NotificationEnum.canary_subscriptions
                ]:
                    futures.append(
                        untrusted_http_request(
                            state=self._state, url=webhook, method="POST", json=warrant
                        )
                    )

        if futures:
            asyncio.gather(*futures)

    def user(self, user_id: ObjectId) -> CanaryUser:
        return CanaryUser(self, user_id)

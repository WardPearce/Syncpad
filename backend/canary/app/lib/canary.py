from ipaddress import ip_address
from typing import TYPE_CHECKING, List

import aiodns
import yarl
from app.env import SETTINGS
from app.errors import (
    CanaryNotFoundException,
    DomainValidationError,
    LocalDomainInvalid,
)
from app.models.canary import CanaryModel
from bson import ObjectId

if TYPE_CHECKING:
    from app.types import State


def __is_local_ip(not_trusted_ip: str):
    ip = ip_address(not_trusted_ip)
    return ip.is_loopback or ip.is_private


async def get_localhost_aliases() -> List[str]:
    aliases = []
    resolver = aiodns.DNSResolver()

    for ip in ("127.0.0.1", "::1"):
        try:
            hostname = await resolver.gethostbyaddr(ip)
            aliases.append(hostname.name)
            aliases.extend(hostname.aliases)
        except aiodns.error.DNSError:
            raise

    return aliases


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

        try:
            txt_records = await self.__upper._resolver.query(
                self.__upper._domain, "TXT"
            )
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
        self._domain = yarl.URL(domain).host
        self._resolver = aiodns.DNSResolver(
            timeout=SETTINGS.canary.domain_verify.timeout
        )
        self._state = state

    def user(self, user_id: ObjectId) -> CanaryUser:
        return CanaryUser(self, user_id)

    async def is_local(self) -> None:
        """Used to validate webhooks if it's a local ip or not.

        Raises:
            LocalDomainInvalid
        """

        if not self._domain:
            raise LocalDomainInvalid()

        localhost_aliases = await get_localhost_aliases()

        if self._domain in localhost_aliases:
            raise LocalDomainInvalid()

        try:
            given_ip = ip_address(self._domain)
            if given_ip.is_private or given_ip.is_loopback:
                raise LocalDomainInvalid()
        except ValueError:
            pass

        try:
            ipv4_address = await self._resolver.query(self._domain, "A")
            for ipv4 in ipv4_address:
                if ipv4 in localhost_aliases or __is_local_ip(ipv4):
                    raise LocalDomainInvalid()

            ipv6_address = await self._resolver.query(self._domain, "AAAA")
            for ipv6 in ipv6_address:
                if ipv6 in localhost_aliases or __is_local_ip(ipv6):
                    raise LocalDomainInvalid()
        except (aiodns.error.DNSError, ValueError):
            raise LocalDomainInvalid()  # Look up fails, assume is private.

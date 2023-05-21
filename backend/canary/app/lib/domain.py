from ipaddress import ip_address
from typing import TYPE_CHECKING, List, cast

import aiodns
import yarl
from app.env import SETTINGS
from app.errors import DomainValidationError, LocalDomainInvalid
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


class Domain:
    def __init__(self, domain: str) -> None:
        self.__domain = yarl.URL(domain).host
        self.__resolver = aiodns.DNSResolver(timeout=SETTINGS.domain_verify.timeout)

    async def attempt_verify(self, state: "State", user_id: ObjectId) -> None:
        """Attempt to verify a canary domain.

        Args:
            state (State)
            user_id (ObjectId)

        Raises:
            DomainValidationError
        """

        if not self.__domain:
            raise DomainValidationError()

        try:
            txt_records = await self.__resolver.query(self.__domain, "TXT")
        except aiodns.error.DNSError:
            raise DomainValidationError()

        canary_code = ""
        for attempts, record in enumerate(txt_records):
            if attempts > 100:
                break

            if record.text.startswith(SETTINGS.domain_verify.prefix):
                canary_code = record.text.replace(SETTINGS.domain_verify.prefix, "", 1)
                break

        canary_code = canary_code.strip()

        if not canary_code:
            raise DomainValidationError()

        canary_search = {"user_id": user_id, "verify.code": canary_code}
        if await state.mongo.canary.count_documents(canary_search) == 0:
            raise DomainValidationError()

        await state.mongo.canary.update_one(
            canary_search, {"$set": {"verify.completed": True}}
        )

    async def is_local(self) -> None:
        """Used to validate webhooks if it's a local ip or not.

        Raises:
            LocalDomainInvalid
        """

        if not self.__domain:
            raise LocalDomainInvalid()

        localhost_aliases = await get_localhost_aliases()

        if self.__domain in localhost_aliases:
            raise LocalDomainInvalid()

        try:
            given_ip = ip_address(self.__domain)
            if given_ip.is_private or given_ip.is_loopback:
                raise LocalDomainInvalid()
        except ValueError:
            pass

        try:
            ipv4_address = await self.__resolver.query(self.__domain, "A")
            for ipv4 in ipv4_address:
                if ipv4 in localhost_aliases or __is_local_ip(ipv4):
                    raise LocalDomainInvalid()

            ipv6_address = await self.__resolver.query(self.__domain, "AAAA")
            for ipv6 in ipv6_address:
                if ipv6 in localhost_aliases or __is_local_ip(ipv6):
                    raise LocalDomainInvalid()
        except (aiodns.error.DNSError, ValueError):
            raise LocalDomainInvalid()  # Look up fails, assume is private.

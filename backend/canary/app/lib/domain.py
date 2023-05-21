from ipaddress import ip_address
from typing import TYPE_CHECKING, List

import aiodns
from app.env import SETTINGS
from app.errors import DomainValidationError
from bson import ObjectId

if TYPE_CHECKING:
    from app.types import State


def is_local_ip(not_trusted_ip: str):
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
        self.__domain = domain
        self.__resolver = aiodns.DNSResolver(timeout=SETTINGS.domain_verify.timeout)

    async def verify(self, state: "State", user_id: ObjectId) -> None:
        if await self.is_local():
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

        if not canary_code:
            raise DomainValidationError()

        canary_search = {"user_id": user_id, "verify.code": canary_code}
        if await state.mongo.canary.count_documents(canary_search) == 0:
            raise DomainValidationError()

        await state.mongo.canary.update_one(
            canary_search, {"$set": {"verify.completed": True}}
        )

    async def is_local(self) -> bool:
        localhost_aliases = await get_localhost_aliases()

        if self.__domain in localhost_aliases:
            return True

        try:
            if ip_address(self.__domain).is_private:
                return True
        except ValueError:
            pass

        try:
            ipv4_address = await self.__resolver.query(self.__domain, "A")
            for ipv4 in ipv4_address:
                if ipv4 in localhost_aliases or is_local_ip(ipv4):
                    return True

            ipv6_address = await self.__resolver.query(self.__domain, "AAAA")
            for ipv6 in ipv6_address:
                if ipv6 in localhost_aliases or is_local_ip(ipv6):
                    return True
        except aiodns.error.DNSError:
            return True  # Look up fails, assume is private.

        return False

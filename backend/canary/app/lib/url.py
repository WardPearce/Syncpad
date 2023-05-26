from ipaddress import ip_address
from typing import TYPE_CHECKING, List

import aiodns
import yarl
from app.errors import LocalDomainInvalid


def __is_local_ip(not_trusted_ip: str):
    ip = ip_address(not_trusted_ip)
    return ip.is_loopback or ip.is_private


async def get_localhost_aliases(resolver: aiodns.DNSResolver) -> List[str]:
    aliases = []
    for ip in ("127.0.0.1", "::1"):
        try:
            hostname = await resolver.gethostbyaddr(ip)
            aliases.append(hostname.name)
            aliases.extend(hostname.aliases)
        except aiodns.error.DNSError:
            raise

    return aliases


async def is_local(url: str) -> None:
    """Used to validate webhooks if it's a local ip or not.

    Raises:
        LocalDomainInvalid
    """

    domain = yarl.URL(url).host

    if not domain:
        raise LocalDomainInvalid()

    resolver = aiodns.DNSResolver()

    localhost_aliases = await get_localhost_aliases(resolver)

    if domain in localhost_aliases:
        raise LocalDomainInvalid()

    try:
        given_ip = ip_address(domain)
        if given_ip.is_private or given_ip.is_loopback:
            raise LocalDomainInvalid()
    except ValueError:
        pass

    try:
        ipv4_address = await resolver.query(domain, "A")
        for ipv4 in ipv4_address:
            if ipv4 in localhost_aliases or __is_local_ip(ipv4):
                raise LocalDomainInvalid()

        ipv6_address = await resolver.query(domain, "AAAA")
        for ipv6 in ipv6_address:
            if ipv6 in localhost_aliases or __is_local_ip(ipv6):
                raise LocalDomainInvalid()
    except (aiodns.error.DNSError, ValueError):
        raise LocalDomainInvalid()  # Look up fails, assume is private.

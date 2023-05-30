from asyncio import wait_for
from ipaddress import ip_address
from typing import TYPE_CHECKING, List, Literal, Union

import aiodns
import yarl
from aiohttp import ClientResponse, ClientTimeout
from aiohttp_proxy import ProxyConnector
from app.errors import LocalDomainInvalid
from env import SETTINGS

if TYPE_CHECKING:
    from app.types import State


async def untrusted_http_request(
    state: "State",
    url: str,
    method: Union[Literal["GET"], Literal["POST"], Literal["DELETE"], Literal["PUT"]],
    **kwargs
) -> ClientResponse:
    kwargs["connector"] = ProxyConnector.from_url(SETTINGS.untrusted_request_proxy)
    # Don't allow redirects
    kwargs["allow_redirects"] = False
    kwargs["timeout"] = ClientTimeout(total=30.0)
    return await wait_for(
        state.aiohttp.request(method=method, url=url, **kwargs),
        # Use wait for timeout to ensure request doesn't
        # last longer then 60 seconds, no matter how aiohttp
        # internals handles their timeout.
        60.0,
    )

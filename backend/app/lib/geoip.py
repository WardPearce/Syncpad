from typing import TYPE_CHECKING, Optional

from app.env import SETTINGS

if TYPE_CHECKING:
    from app.custom_types import State


class GeoIp:
    def __init__(self, state: "State", ip: str) -> None:
        self._state = state
        self._ip = ip

    async def get(self) -> Optional[dict]:
        if not SETTINGS.proxy_check:
            return

        resp = await self._state.aiohttp.get(
            url=f"{SETTINGS.proxy_check.url}/{self._ip}",
            params={"key": SETTINGS.proxy_check.api_key, "asn": "1"},
        )

        if not resp.status == 200:
            return

        resp_json = await resp.json()
        if resp_json["status"] != "ok":
            return

        return resp_json[self._ip]

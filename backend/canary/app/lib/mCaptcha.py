from typing import TYPE_CHECKING, Optional

from app.env import SETTINGS
from errors import InvalidCaptcha

if TYPE_CHECKING:
    from custom_types import State


async def validate_captcha(state: "State", token: Optional[str]) -> None:
    if SETTINGS.mcaptcha is None:
        return

    if not token:
        raise InvalidCaptcha()

    resp = await state.aiohttp.post(
        SETTINGS.mcaptcha.verify_url,
        json={
            "token": token,
            "key": SETTINGS.mcaptcha.site_key,
            "secret": SETTINGS.mcaptcha.account_secret,
        },
    )
    if resp.status != 200:
        # Let user pass if our service is down.
        return

    if not (await resp.json())["valid"]:
        raise InvalidCaptcha()

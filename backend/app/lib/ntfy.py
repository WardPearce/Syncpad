from typing import TYPE_CHECKING, Literal

from app.env import SETTINGS

if TYPE_CHECKING:
    from app.custom_types import State


async def push_notification(
    state: "State",
    topic: str,
    message: str,
    title: str,
    tags: str,
    priority: Literal["default"]
    | Literal["max"]
    | Literal["high"]
    | Literal["low"]
    | Literal["min"] = "default",
) -> None:
    await state.aiohttp.post(
        f"{SETTINGS.ntfy.url}/{topic}",
        data=message,
        headers={
            "Title": title,
            "Priority": priority,
            "Tags": tags,
        },
    )

from typing import TYPE_CHECKING, cast

from app.env import SETTINGS
from litestar import Litestar
from motor import motor_asyncio

if TYPE_CHECKING:
    from app.types import State


async def init_mongo(state: "State") -> motor_asyncio.AsyncIOMotorCollection:
    if not getattr("state", "mongo", None):
        mongo = motor_asyncio.AsyncIOMotorClient(
            SETTINGS.mongo.host, SETTINGS.mongo.port
        )
        await mongo.server_info(None)
        state.mongo = cast(
            motor_asyncio.AsyncIOMotorCollection, mongo[SETTINGS.mongo.collection]
        )

    return state.mongo


app = Litestar(route_handlers=[], on_startup=[init_mongo])

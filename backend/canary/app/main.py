from typing import TYPE_CHECKING, cast

import aiohttp
from app.controllers import routes
from app.env import SETTINGS
from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.config.csrf import CSRFConfig
from litestar.config.response_cache import ResponseCacheConfig
from litestar.openapi import OpenAPIConfig
from litestar.stores.redis import RedisStore
from motor import motor_asyncio
from redis.asyncio import Redis

if TYPE_CHECKING:
    from app.types import State


cache_store = RedisStore(
    redis=Redis(
        host=SETTINGS.redis.host, port=SETTINGS.redis.port, db=SETTINGS.redis.db
    )
)


async def init_mongo(state: "State") -> motor_asyncio.AsyncIOMotorCollection:
    if not getattr(state, "mongo", None):
        mongo = motor_asyncio.AsyncIOMotorClient(
            SETTINGS.mongo.host, SETTINGS.mongo.port
        )
        await mongo.server_info(None)
        state.mongo = cast(
            motor_asyncio.AsyncIOMotorCollection, mongo[SETTINGS.mongo.collection]
        )

        await state.mongo.old_otp.create_index("expires", expireAfterSeconds=0)

    return state.mongo


async def init_aiohttp(state: "State") -> aiohttp.ClientSession:
    if not getattr(state, "aiohttp", None):
        state.aiohttp = aiohttp.ClientSession()

    return state.aiohttp


async def deconstruct_aiohttp(state: "State") -> None:
    await state.aiohttp.close()


async def init_redis(state: "State") -> RedisStore:
    if not getattr(state, "redis", None):
        state.redis = cache_store

    return state.redis


async def wipe_cache_on_shutdown() -> None:
    await cache_store.delete_all()


app = Litestar(
    route_handlers=[routes],
    on_startup=[init_mongo, init_redis, init_aiohttp],
    on_shutdown=[deconstruct_aiohttp],
    csrf_config=CSRFConfig(
        secret=SETTINGS.csrf_secret,
        cookie_httponly=False,
    ),
    cors_config=CORSConfig(
        allow_origins=[SETTINGS.proxy_urls.backend, SETTINGS.proxy_urls.frontend],
        allow_credentials=True,
    ),
    openapi_config=OpenAPIConfig(
        title=SETTINGS.open_api.title, version=SETTINGS.open_api.version
    ),
    response_cache_config=ResponseCacheConfig(store=cache_store),
    before_shutdown=[wipe_cache_on_shutdown],
)

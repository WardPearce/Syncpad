from typing import TYPE_CHECKING, cast

import aiohttp
from app.controllers import routes
from app.env import SETTINGS
from app.lib.jwt import jwt_cookie_auth
from app.models.customs import CustomJsonEncoder
from app.tasks import tasks
from lib.tasks import CronTabs
from litestar import Litestar
from litestar.config.cors import CORSConfig
from litestar.config.csrf import CSRFConfig
from litestar.config.response_cache import ResponseCacheConfig
from litestar.connection.request import Request
from litestar.middleware.rate_limit import RateLimitConfig
from litestar.openapi import OpenAPIConfig, OpenAPIController
from litestar.openapi.spec import License, Server
from litestar.stores.redis import RedisStore
from motor import motor_asyncio
from pydantic import BaseModel
from redis.asyncio import Redis

if TYPE_CHECKING:
    from custom_types import State

redis = Redis(host=SETTINGS.redis.host, port=SETTINGS.redis.port, db=SETTINGS.redis.db)
cache_store = RedisStore(redis=redis)


async def init_tasks(state: "State") -> CronTabs:
    if not getattr(state, "tasks", None):
        state.tasks = CronTabs(state, tasks)
        state.tasks.start()

    return state.tasks


async def close_tasks(state: "State") -> None:
    state.tasks.stop()


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
        await state.mongo.proof.create_index("expires", expireAfterSeconds=0)
        await state.mongo.session.create_index("record_kept_till", expireAfterSeconds=0)
        await state.mongo.email_verification.create_index(
            "expires", expireAfterSeconds=0
        )
        await state.mongo.canary_warrant.create_index(
            "issued",
            expireAfterSeconds=10800,  # 3 hours
            partialFilterExpression={"active": False},
        )

    return state.mongo


async def init_aiohttp(state: "State") -> aiohttp.ClientSession:
    if not getattr(state, "aiohttp", None):
        state.aiohttp = aiohttp.ClientSession()

    return state.aiohttp


async def close_aiohttp(state: "State") -> None:
    await state.aiohttp.close()


async def init_redis(state: "State") -> RedisStore:
    if not getattr(state, "redis", None):
        state.redis = cache_store
        await redis.ping()

    return state.redis


async def wipe_cache_on_shutdown() -> None:
    await cache_store.delete_all()
    await redis.close()


class OpenAPIControllerRouteFix(OpenAPIController):
    def render_stoplight_elements(self, request: Request) -> str:
        # Gross hack to overwrite the path for the openapi schema file.
        # due to reverse proxying.
        path_copy = str(self.path)
        self.path = SETTINGS.proxy_urls.backend + self.path

        render = super().render_stoplight_elements(request)

        self.path = path_copy
        return render


app = Litestar(
    route_handlers=[routes],
    on_startup=[init_mongo, init_redis, init_aiohttp, init_tasks],
    on_shutdown=[close_aiohttp, wipe_cache_on_shutdown, close_tasks],
    csrf_config=CSRFConfig(
        secret=SETTINGS.csrf_secret, cookie_httponly=False, cookie_samesite="strict"
    ),
    middleware=[
        RateLimitConfig(rate_limit=("minute", 60), exclude=["/schema"]).middleware
    ],
    cors_config=CORSConfig(
        allow_origins=[SETTINGS.proxy_urls.backend, SETTINGS.proxy_urls.frontend],
        allow_credentials=True,
    ),
    openapi_config=OpenAPIConfig(
        title=SETTINGS.open_api.title,
        create_examples=True,
        root_schema_site="elements",
        enabled_endpoints={"elements", "openapi.json", "openapi.yaml"},
        license=License(
            name="GNU Affero General Public License v3.0",
            identifier="AGPL-3.0",
            url="https://github.com/WardPearce/Purplix.io/blob/main/LICENSE",
        ),
        openapi_controller=OpenAPIControllerRouteFix,
        terms_of_service=f"{SETTINGS.proxy_urls.frontend}/terms-of-service",
        version=SETTINGS.open_api.version,
        servers=[Server(url=SETTINGS.proxy_urls.backend, description="Production API")],
    ),
    response_cache_config=ResponseCacheConfig(store=cache_store),
    on_app_init=[jwt_cookie_auth.on_app_init],
    type_encoders={
        BaseModel: lambda m: m.dict(by_alias=True),
        **CustomJsonEncoder.Config.json_encoders,
    },
    debug=SETTINGS.proxy_urls.frontend == "localhost",
)

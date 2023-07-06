from aiohttp import ClientSession
from litestar.datastructures.state import State as BaseState
from litestar.stores.redis import RedisStore
from motor import motor_asyncio

from app.lib.tasks import CronTasks


class State(BaseState):
    mongo: motor_asyncio.AsyncIOMotorCollection
    redis: RedisStore
    aiohttp: ClientSession
    tasks: CronTasks

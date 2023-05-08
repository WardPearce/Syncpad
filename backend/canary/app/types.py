from litestar.datastructures.state import State as BaseState
from litestar.stores.redis import RedisStore
from motor import motor_asyncio


class State(BaseState):
    mongo: motor_asyncio.AsyncIOMotorCollection
    redis: RedisStore

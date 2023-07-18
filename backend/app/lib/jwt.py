from typing import TYPE_CHECKING, Optional, cast

from bson.objectid import ObjectId
from litestar.connection import ASGIConnection
from litestar.contrib.jwt import JWTCookieAuth, Token

from app.env import SETTINGS

if TYPE_CHECKING:
    from app.custom_types import State


async def delete_all_user_sessions(state: "State", user_id: ObjectId) -> None:
    search = {"user_id": user_id}

    async for session in state.mongo.session.find(search):
        await state.redis.delete(str(session["_id"]))

    await state.mongo.session.delete_many(search)


async def delete_session(
    state: "State", session_id: ObjectId, user_id: ObjectId
) -> None:
    search = {"_id": session_id, "user_id": user_id}
    if await state.mongo.session.count_documents(search) > 0:
        await state.mongo.session.delete_one(search)
        await state.redis.delete(str(session_id))


async def retrieve_user_handler(
    token: Token, connection: ASGIConnection
) -> Optional[ObjectId]:
    state = cast("State", connection.scope["app"].state)
    jti = cast(str, token.jti)

    whitelisted = await state.redis.get(jti)

    if whitelisted is None:
        if await state.mongo.session.count_documents({"_id": ObjectId(jti)}) > 0:
            await state.redis.set(jti, "true", 360)

            return ObjectId(token.sub)
        else:
            await state.redis.set(jti, "false", SETTINGS.jwt.expire_days * 86400)
            return None
    elif whitelisted == b"true":
        return ObjectId(token.sub)
    else:
        return None


jwt_cookie_auth = JWTCookieAuth[ObjectId](
    retrieve_user_handler=retrieve_user_handler,
    token_secret=SETTINGS.jwt.secret,
    exclude=[
        "/schema",
    ],
    samesite="strict",
    secure=SETTINGS.proxy_urls.frontend != "localhost",
)

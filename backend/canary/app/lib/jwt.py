from typing import TYPE_CHECKING, Any, Optional, cast

from app.env import SETTINGS
from bson.objectid import ObjectId
from litestar.connection import ASGIConnection
from litestar.contrib.jwt import JWTCookieAuth, Token
from pydantic import BaseModel

if TYPE_CHECKING:
    from app.types import State


async def retrieve_user_handler(
    token: Token, connection: ASGIConnection
) -> Optional[ObjectId]:
    state = cast("State", connection.scope["app"].state)
    jti = cast(str, token.jti)

    blacklisted = await state.redis.get(jti)

    if blacklisted is None:
        if await state.mongo.jwt_blacklist.count_documents({"_id": token.jti}) > 0:
            # Cache is blacklisted for 32 hours.
            await state.redis.set(jti, "true", 115200)
            return None

        user_id = ObjectId(token.sub)
        if await state.mongo.user.count_documents({"_id": user_id}) > 0:
            await state.redis.set(jti, "false", 60)
            return user_id

        return None
    elif blacklisted == "true":  # Is stored as a string.
        return None
    else:
        return ObjectId(token.sub)


jwt_cookie_auth = JWTCookieAuth[ObjectId](
    retrieve_user_handler=retrieve_user_handler,
    token_secret=SETTINGS.jwt.secret,
    exclude=[
        "/schema",
    ],
    samesite="strict",
    secure=SETTINGS.proxy_urls.frontend != "localhost",
)

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

    whitelisted = await state.redis.get(jti)

    if whitelisted is None:
        if await state.mongo.session.count_documents({"_id": ObjectId(jti)}) > 0:
            await state.redis.set(jti, "true", 60)

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

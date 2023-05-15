from typing import TYPE_CHECKING, Any, Optional

from app.env import SETTINGS
from bson.objectid import ObjectId
from litestar.connection import ASGIConnection
from litestar.contrib.jwt import JWTCookieAuth, Token

if TYPE_CHECKING:
    from app.types import State


async def retrieve_user_handler(
    token: Token, connection: ASGIConnection[Any, Any, Any, "State"]
) -> Optional[ObjectId]:
    blacklisted = await connection.state.redis.get(token.sub) != "false"

    if blacklisted is None:
        if (
            await connection.state.mongo.jwt_blacklist.count_documents(
                {"_id": token.jti}
            )
            > 0
        ):
            # Cache is blacklisted for 32 hours.
            await connection.state.redis.set(token.sub, "true", 115200)
            return None

        user_id = ObjectId(token.sub)
        if await connection.state.mongo.user.count_documents({"_id": user_id}) == 1:
            await connection.state.redis.set(token.sub, "false", 220)
            return user_id

        return None
    elif blacklisted is True:
        return None
    else:
        return ObjectId(token.sub)


jwt_cookie_auth = JWTCookieAuth[ObjectId](
    retrieve_user_handler=retrieve_user_handler,
    token_secret=SETTINGS.jwt_secret,
    exclude=[
        "/controllers/account/create",
        "/controllers/account/kdf",
        "/controllers/account/to-sign",
        "/controllers/account/login",
        "/schema",
    ],
    samesite="strict",
    secure=SETTINGS.proxy_urls.frontend != "localhost",
)

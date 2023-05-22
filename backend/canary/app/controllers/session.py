from typing import TYPE_CHECKING, Any, List

from app.models.session import SessionModel
from bson import ObjectId
from litestar import Request, Router, get
from litestar.contrib.jwt import Token

if TYPE_CHECKING:
    from app.types import State


@get(path="/", description="List active sessions", tags=["session"])
async def get_sessions(
    request: Request[ObjectId, Token, Any], state: "State"
) -> List[SessionModel]:
    sessions = []
    async for session in state.mongo.session.find({"user_id": request.user}):
        sessions.append(SessionModel(**session))

    return sessions


router = Router(path="/session", route_handlers=[get_sessions])

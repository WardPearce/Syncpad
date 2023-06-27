from typing import TYPE_CHECKING, Any, List

from app.lib.jwt import delete_session
from app.models.session import SessionModel
from bson import ObjectId
from bson.errors import InvalidId
from litestar import Request, Router, delete, get
from litestar.contrib.jwt import Token

if TYPE_CHECKING:
    from custom_types import State


@get(path="/", description="List active sessions", tags=["session"])
async def get_sessions(
    request: Request[ObjectId, Token, Any], state: "State"
) -> List[SessionModel]:
    sessions = []
    async for session in state.mongo.session.find({"user_id": request.user}).sort(
        "created", -1
    ):
        sessions.append(SessionModel(**session))

    return sessions


@delete(path="/{session_id:str}", description="Invalidate a session", tags=["session"])
async def invalidate_session(
    request: Request[ObjectId, Token, Any], state: "State", session_id: str
) -> None:
    try:
        await delete_session(state, ObjectId(session_id), request.user)
    except InvalidId:
        pass


router = Router(path="/session", route_handlers=[get_sessions, invalidate_session])

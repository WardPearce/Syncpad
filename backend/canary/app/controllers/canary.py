import secrets
from datetime import datetime
from typing import TYPE_CHECKING, Annotated, Any

from app.errors import DomainTaken
from app.models.canary import CanaryModel, CreateCanaryModel
from bson import ObjectId
from litestar import Controller, Request, Router, post, put
from litestar.contrib.jwt import Token
from litestar.datastructures import UploadFile
from litestar.enums import RequestEncodingType
from litestar.params import Body

if TYPE_CHECKING:
    from app.types import State


@post(path="/create", description="Create a canary for a given domain", tags=["canary"])
async def create_canary(
    data: CreateCanaryModel, state: "State", request: Request[ObjectId, Token, Any]
) -> CanaryModel:
    domain = data.domain.lower()

    if (
        await state.mongo.canary.count_documents(
            {"domain": domain, "domain_verification.completed": True}
        )
        > 0
    ):
        raise DomainTaken()

    to_insert = {
        **data.dict(),
        "user_id": request.user,
        "created": datetime.now(),
        "domain_verification": {"completed": False, "code": secrets.token_urlsafe(32)},
    }

    await state.mongo.canary.insert_one(to_insert)

    return CanaryModel(**to_insert)


class CanaryController(Controller):
    path = "/{domain:str}"

    @put("/logo/update", description="Update logo for given domain", tags=["canary"])
    async def update_logo(
        self,
        domain: str,
        data: Annotated[UploadFile, Body(media_type=RequestEncodingType.MULTI_PART)],
    ) -> None:
        await data.read()


router = Router(path="/canary", route_handlers=[create_canary, CanaryController])

import pathlib
import secrets
from datetime import datetime
from typing import TYPE_CHECKING, Annotated, Any, List

from app.env import SETTINGS
from app.errors import (
    CanaryTaken,
    DomainValidationError,
    FileTooBig,
    UnsupportedFileType,
)
from app.lib.canary import Canary
from app.lib.s3 import format_path, s3_create_client
from app.models.canary import CanaryModel, CreateCanaryModel, PublicCanaryModel
from bson import ObjectId
from litestar import Controller, Request, Response, Router, get, post
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
            {
                "$or": [
                    {"domain": domain, "domain_verification.completed": True},
                    {"domain": domain, "user_id": request.user},
                ]
            }
        )
        > 0
    ):
        raise CanaryTaken()

    to_insert = {
        **data.dict(),
        "domain": domain,
        "user_id": request.user,
        "created": datetime.now(),
        "logo": None,
        "domain_verification": {"completed": False, "code": secrets.token_urlsafe(32)},
    }

    await state.mongo.canary.insert_one(to_insert)

    return CanaryModel(**to_insert)


@get("/list", description="List canaries for user", tags=["canary"])
async def list_canaries(
    request: Request[ObjectId, Token, Any], state: "State"
) -> List[CanaryModel]:
    canaries: List[CanaryModel] = []
    async for canary in state.mongo.canary.find({"user_id": request.user}):
        canaries.append(CanaryModel(**canary))

    return canaries


class CanaryController(Controller):
    path = "/{domain:str}"

    @post("/verify", description="Verify domain ownership via DNS", tags=["canary"])
    async def verify(
        self, domain: str, request: Request[ObjectId, Token, Any], state: "State"
    ) -> Response:
        try:
            await Canary(state, domain).user(request.user).attempt_verify()
        except DomainValidationError:
            raise

        return Response(content=None, status_code=200)

    @get(
        "/public",
        description="Get public details about canary",
        tags=["canary"],
        exclude_from_auth=True,
    )
    async def public_canary(self, domain: str, state: "State") -> PublicCanaryModel:
        return await Canary(state, domain).get()

    @get("/", description="Get private details about a canary", tags=["canary"])
    async def get_canary(
        self, domain: str, request: Request[ObjectId, Token, Any], state: "State"
    ) -> CanaryModel:
        return await Canary(state, domain).user(request.user).get()

    @post("/logo/update", description="Update logo for given domain", tags=["canary"])
    async def update_logo(
        self,
        domain: str,
        request: Request[ObjectId, Token, Any],
        state: "State",
        data: Annotated[
            List[UploadFile], Body(media_type=RequestEncodingType.MULTI_PART)
        ],
    ) -> None:
        logo_ext = pathlib.Path(data[0].filename).suffix
        if logo_ext not in SETTINGS.canary.logo.allowed_extensions:
            raise UnsupportedFileType()

        canary = await Canary(state, domain).user(request.user).get()

        logo = await data[0].read(SETTINGS.canary.logo.max_size + 24)
        if len(logo) > SETTINGS.canary.logo.max_size:
            raise FileTooBig()

        logo_filename = f"{canary.id}{logo_ext}"

        async with s3_create_client() as s3:
            await s3.put_object(
                Bucket=SETTINGS.s3.bucket,
                Key=format_path("canary", "logos", logo_filename),
                Body=logo,
            )

        await state.mongo.canary.update_one(
            {"_id": canary.id}, {"$set": {"logo": logo_filename}}
        )


router = Router(
    path="/canary", route_handlers=[create_canary, list_canaries, CanaryController]
)

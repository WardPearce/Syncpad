import hashlib
import pathlib
import secrets
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Annotated, Any, Dict, List, Optional

from app.env import SETTINGS
from app.errors import (
    CanaryAlreadyTrusted,
    CanaryNotFoundException,
    CanaryTaken,
    DomainValidationError,
    FileTooBig,
    PublishedWarrantNotFoundException,
    UnsupportedFileType,
)
from app.lib.canary import Canary
from app.lib.otp import OneTimePassword
from app.lib.s3 import format_path, s3_create_client
from app.lib.user import User
from app.models.canary import (
    CanaryModel,
    CreateCanaryModel,
    CreateCanaryWarrantModel,
    CreatedCanaryWarrantModel,
    NextCanaryEnum,
    PublicCanaryModel,
    PublishCanaryWarrantModel,
    PublishedCanaryWarrantModel,
    TrustedCanaryModel,
)
from bson import ObjectId
from bson.errors import InvalidId
from lib.otp import OneTimePassword
from litestar import Controller, Request, Response, Router, delete, get, post
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
    domain = data.domain.lower().strip()

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
        or await state.mongo.deleted_canary.count_documents(
            {"domain_hash": hashlib.sha256(domain.encode()).hexdigest()}
        )
        > 0
    ):
        raise CanaryTaken()

    to_insert = {
        **data.dict(),
        "domain": domain,
        "user_id": request.user,
        "created": datetime.utcnow(),
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


@get("/trusted/list", description="List trusted canaries", tags=["canary"])
async def list_trusted_canaries(
    request: Request[ObjectId, Token, Any], state: "State"
) -> Dict[str, TrustedCanaryModel]:
    trusted_canaries: Dict[str, TrustedCanaryModel] = {}

    async for trusted in state.mongo.trusted_canary.find({"user_id": request.user}):
        trusted_canaries[trusted["domain"]] = TrustedCanaryModel(**trusted)

    return trusted_canaries


@get(
    "/published/{canary_id:str}/{page:int}",
    description="Get a canary warrant",
    tags=["canary", "warrant"],
    exclude_from_auth=True,
)
async def published_warrant(
    state: "State", canary_id: str, page: int = 0
) -> PublishedCanaryWarrantModel:
    try:
        canary_object_id = ObjectId(canary_id)
    except InvalidId:
        raise PublishedWarrantNotFoundException()

    warrant = await state.mongo.canary_warrant.find_one(
        {"canary_id": canary_object_id, "concern": {"$exists": True}},
        sort=[("_id", -1)],
        skip=page,
    )
    if not warrant:
        raise PublishedWarrantNotFoundException()

    return PublishedCanaryWarrantModel(**warrant)


class PublishCanary(Controller):
    path = "/warrant/{id_:str}"

    @post("/publish", description="Publish a canary", tags=["canary", "warrant"])
    async def publish(
        self,
        request: Request[ObjectId, Token, Any],
        state: "State",
        id_: str,
        data: PublishCanaryWarrantModel,
    ) -> None:
        try:
            warrant_id = ObjectId(id_)
        except InvalidId:
            raise PublishedWarrantNotFoundException()

        warrant = await state.mongo.canary_warrant.find_one(
            {"_id": warrant_id, "user_id": request.user, "active": False}
        )
        if not warrant:
            raise PublishedWarrantNotFoundException()

        await state.mongo.canary_warrant.update_one(
            {
                "_id": warrant_id,
                "user_id": request.user,
                "active": False,
            },
            {
                "$set": {**data.dict(), "concern": data.concern.value, "active": True},
            },
        )

        await state.mongo.canary_warrant.update_many(
            {"canary_id": warrant["canary_id"], "_id": {"$ne": warrant_id}},
            {"$set": {"active": False}},
        )


class CanarySubscription(Controller):
    path = "/subscription/{canary_id:str}"

    @get(
        "/",
        description="Check if user is subscribed to a canary",
        tags=["canary", "subscription"],
    )
    async def am_subscribed(
        self, request: Request[ObjectId, Token, Any], state: "State", canary_id: str
    ) -> bool:
        try:
            id_ = ObjectId(canary_id)
        except InvalidId:
            return False

        return (
            await state.mongo.subscribed_canary.count_documents(
                {"user_id": request.user, "canary_id": id_}
            )
            > 0
        )

    @delete(
        "/unsubscribe",
        description="Unsubscribe from a canary",
        tags=["canary", "subscription"],
    )
    async def unsubscribe(
        self,
        request: Request[ObjectId, Token, Any],
        state: "State",
        canary_id: str,
    ) -> None:
        try:
            id_ = ObjectId(canary_id)
        except InvalidId:
            return

        await state.mongo.subscribed_canary.delete_one(
            {
                "user_id": request.user,
                "canary_id": id_,
            }
        )

    @post(
        "/subscribe",
        description="Subscribe to a canary",
        tags=["canary", "subscription"],
    )
    async def subscribe(
        self,
        request: Request[ObjectId, Token, Any],
        state: "State",
        canary_id: str,
    ) -> None:
        try:
            id_ = ObjectId(canary_id)
        except InvalidId:
            return

        if (
            await state.mongo.subscribed_canary.count_documents(
                {"user_id": request.user, "canary_id": id_}
            )
            == 0
        ):
            await state.mongo.subscribed_canary.insert_one(
                {
                    "user_id": request.user,
                    "canary_id": id_,
                }
            )


class CanaryController(Controller):
    path = "/{domain:str}"

    @post(
        "/create/warrant",
        description="Create a warrant for a canary",
        tags=["canary", "warrant"],
    )
    async def create_warrant(
        self,
        request: Request[ObjectId, Token, Any],
        state: "State",
        domain: str,
        data: CreateCanaryWarrantModel,
        otp: str,
    ) -> CreatedCanaryWarrantModel:
        canary = await Canary(state, domain).user(request.user).get()
        if not canary.domain_verification.completed:
            raise DomainValidationError()

        user = await User(state, request.user).get()
        await OneTimePassword.validate_user(state, user, otp)

        now: datetime = datetime.utcnow()
        match data.next_:
            case NextCanaryEnum.tomorrow:
                next_canary = now + timedelta(days=1)
            case NextCanaryEnum.week:
                next_canary = now + timedelta(days=7)
            case NextCanaryEnum.fortnight:
                next_canary = now + timedelta(days=14)
            case NextCanaryEnum.month:
                next_canary = now + timedelta(days=30)
            case NextCanaryEnum.quarter:
                next_canary = now + timedelta(days=90)
            case _:
                next_canary = now + timedelta(days=365)

        created_warrant = {
            "user_id": request.user,
            "canary_id": canary.id,
            "next_canary": next_canary,
            "issued": now,
            "active": False,
        }

        await state.mongo.canary_warrant.insert_one(created_warrant)

        return CreatedCanaryWarrantModel(**created_warrant)

    @get(
        "/trusted",
        description="Get signed public key hash for a trusted canary",
        tags=["canary"],
    )
    async def get_trusted(
        self, request: Request[ObjectId, Token, Any], state: "State", domain: str
    ) -> TrustedCanaryModel:
        trusted = await state.mongo.trusted_canary.find_one(
            {"user_id": request.user, "domain": domain}
        )
        if not trusted:
            raise CanaryNotFoundException()

        return TrustedCanaryModel(**trusted)

    @post(
        "/trusted/add",
        description="Saves a canary as a trusted canary",
        tags=["canary"],
    )
    async def trust_canary(
        self,
        request: Request[ObjectId, Token, Any],
        state: "State",
        data: TrustedCanaryModel,
        domain: str,
    ) -> None:
        try:
            await Canary(state, domain).exists()
        except CanaryNotFoundException:
            raise

        if (
            await state.mongo.trusted_canary.count_documents(
                {"user_id": request.user, "domain": domain}
            )
            > 0
        ):
            raise CanaryAlreadyTrusted()

        trusted = {"user_id": request.user, "domain": domain, **data.dict()}
        await state.mongo.trusted_canary.insert_one(trusted)

    @post("/verify", description="Verify domain ownership via DNS", tags=["canary"])
    async def verify(
        self, domain: str, request: Request[ObjectId, Token, Any], state: "State"
    ) -> Response:
        try:
            await Canary(state, domain).user(request.user).attempt_verify()
        except DomainValidationError:
            raise

        return Response(content=None, status_code=200)

    @delete("/delete", description="Delete a canary", tags=["canary"])
    async def delete_canary(
        self,
        domain: str,
        request: Request[ObjectId, Token, Any],
        state: "State",
        otp: str,
    ) -> None:
        user = await User(state, request.user).get()
        await OneTimePassword.validate_user(state, user, otp)

        await Canary(state, domain).user(request.user).delete()

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
    path="/canary",
    route_handlers=[
        create_canary,
        list_canaries,
        list_trusted_canaries,
        published_warrant,
        PublishCanary,
        CanaryController,
        CanarySubscription,
    ],
)

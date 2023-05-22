import secrets
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Any, Optional, cast

import pyotp
from app.errors import (
    EmailTaken,
    InvalidAccountAuth,
    InvalidCaptcha,
    OtpAlreadyCompleted,
    UserNotFoundException,
)
from app.lib.jwt import jwt_cookie_auth
from app.lib.otp import OneTimePassword
from app.lib.user import User
from app.models.jwt import UserJtiModel
from app.models.session import CreateSessionModel, SessionLocationModel
from app.models.user import (
    CreateUserModel,
    OtpModel,
    PublicUserModel,
    UserLoginSignatureModel,
    UserModel,
    UserToSignModel,
)
from bson import ObjectId
from env import SETTINGS
from lib.mCaptcha import validate_captcha
from litestar import Request, Response, Router, delete
from litestar.contrib.jwt import Token
from litestar.controller import Controller
from litestar.exceptions import ValidationException
from litestar.handlers import get, post
from nacl.encoding import Base64Encoder
from nacl.exceptions import BadSignatureError
from nacl.public import PublicKey, SealedBox
from nacl.signing import VerifyKey

if TYPE_CHECKING:
    from app.types import State


class LoginController(Controller):
    path = "/{email:str}"

    @get(
        path="/public",
        description="Public KDF details",
        tags=["account"],
        exclude_from_auth=True,
    )
    async def public(self, state: "State", email: str) -> PublicUserModel:
        user = await User(state, email).get()

        return PublicUserModel(kdf=user.kdf, otp_completed=user.otp.completed)

    @get(
        path="/to-sign",
        description="Used to generate a unique code to sign.",
        tags=["account"],
        raises=[UserNotFoundException],
        exclude_from_auth=True,
    )
    async def to_sign(self, state: "State", email: str) -> UserToSignModel:
        try:
            user = await User(state, email).get()
        except UserNotFoundException:
            raise
        else:
            to_sign = secrets.token_urlsafe(32)
            result = await state.mongo.proof.insert_one(
                {
                    "to_sign": to_sign,
                    "user_id": ObjectId(user.id),
                    "expires": datetime.now(tz=timezone.utc) + timedelta(seconds=60),
                }
            )
            return UserToSignModel(to_sign=to_sign, _id=result.inserted_id)

    @post(
        path="/login",
        description="Validate signature and OTP code",
        tags=["account"],
        raises=[InvalidCaptcha, InvalidAccountAuth],
        exclude_from_auth=True,
    )
    async def login(
        self,
        state: "State",
        request: Request,
        captcha: str,
        otp: Optional[str],
        data: UserLoginSignatureModel,
        email: str,
    ) -> Response[UserJtiModel]:
        user = await User(state, email).get()

        proof_search = {"user_id": ObjectId(user.id), "_id": ObjectId(data.id)}
        proof = await state.mongo.proof.find_one(proof_search)
        if not proof:
            raise InvalidAccountAuth()

        await state.mongo.proof.delete_one(proof_search)

        try:
            await validate_captcha(state, captcha)
        except InvalidCaptcha:
            raise

        if user.otp.completed:
            try:
                await OneTimePassword.validate_user(state, user, otp)
            except InvalidAccountAuth:
                raise

        try:
            public_key = Base64Encoder.decode(user.auth.public_key.encode())
        except ValueError:
            raise InvalidAccountAuth()

        try:
            given_code = VerifyKey(public_key).verify(
                Base64Encoder.decode(data.signature.encode())
            )
        except (BadSignatureError, ValueError):
            raise InvalidAccountAuth()

        # Not open to timing attacks, one use code.
        if given_code.decode() != proof["to_sign"]:
            raise InvalidAccountAuth()

        now = datetime.now(tz=timezone.utc)
        token_timedelta = timedelta(days=SETTINGS.jwt.expire_days)

        location = SessionLocationModel()
        device: Optional[str] = None

        try:
            sealed_box = SealedBox(
                PublicKey(Base64Encoder.decode(user.keypair.public_key.encode()))
            )
        except ValueError:
            pass
        else:
            if (
                user.ip_lookup_consent
                and SETTINGS.proxy_check
                and request.client
                and request.client.host
            ):
                client_ip = request.client.host

                resp = await state.aiohttp.get(
                    url=f"{SETTINGS.proxy_check.url}/{client_ip}",
                    params={"key": SETTINGS.proxy_check.api_key, "asn": "1"},
                )
                if resp.status == 200:
                    resp_json = await resp.json()
                    if resp_json["status"] == "ok":
                        location = SessionLocationModel(
                            region=Base64Encoder.encode(
                                sealed_box.encrypt(
                                    cast(
                                        str,
                                        resp_json[client_ip].get("region", "Unknown"),
                                    ).encode()
                                )
                            ).decode(),
                            country=Base64Encoder.encode(
                                sealed_box.encrypt(
                                    cast(
                                        str,
                                        resp_json[client_ip].get("country", "Unknown"),
                                    ).encode()
                                )
                            ).decode(),
                            ip=Base64Encoder.encode(
                                sealed_box.encrypt(client_ip.encode())
                            ).decode(),
                        )

            if "User-Agent" in request.headers:
                device = Base64Encoder.encode(
                    sealed_box.encrypt(request.headers["User-Agent"].encode())
                ).decode()

        session = await state.mongo.session.insert_one(
            CreateSessionModel(
                expires=now + token_timedelta,
                record_kept_till=now + timedelta(days=SETTINGS.jwt.expire_days * 7),
                created=now,
                location=location,
                device=device,
                user_id=user.id,
            ).dict()
        )

        return jwt_cookie_auth.login(
            identifier=str(user.id),
            token_expiration=token_timedelta,
            response_body=UserJtiModel(jti=session.inserted_id, user=user),
            token_unique_jwt_id=str(session.inserted_id),
        )


@post(
    path="/create",
    description="Create a user account",
    tags=["account"],
    status_code=201,
    exclude_from_auth=True,
)
async def create_account(
    state: "State", captcha: str, data: CreateUserModel
) -> Response:
    try:
        await validate_captcha(state, captcha)
    except InvalidCaptcha:
        raise

    email = data.email.lower()  # Ensure always lowercase email.

    if await state.mongo.user.count_documents({"email": email}) > 0:
        raise EmailTaken()

    await state.mongo.user.insert_one(
        {
            **data.dict(),
            "created": datetime.now(),
            "otp": {"secret": pyotp.random_base32(), "completed": False},
        }
    )

    return Response(None, status_code=201)


@get(
    path="/me",
    description="Get JWT sub for user",
    tags=["account"],
    sync_to_thread=False,
)
def me(request: Request[ObjectId, Token, Any]) -> str:
    return str(request.user)


class OtpController(Controller):
    path = "/otp"

    @post(
        path="/setup",
        description="Used to confirm OTP is completed",
        tags=["account"],
        status_code=201,
        raises=[OtpAlreadyCompleted],
    )
    async def otp_setup(
        self, request: Request[ObjectId, Token, Any], state: "State", otp: str
    ) -> Response:
        user = await User(state, request.user).get()

        if user.otp.completed:
            raise OtpAlreadyCompleted()

        try:
            await OneTimePassword.validate_user(state, user, otp)
        except InvalidAccountAuth:
            # Not defined in errors.py because it should
            # only be used here.
            raise ValidationException(detail="Invalid OTP code")

        await state.mongo.user.update_one(
            {"_id": ObjectId(user.id)}, {"$set": {"otp.completed": True}}
        )

        return Response(None, status_code=201)

    @delete(path="/reset", description="Reset OTP", tags=["account"], status_code=200)
    async def reset_otp(
        self, state: "State", request: Request[ObjectId, Token, Any], otp: str
    ) -> OtpModel:
        user = await User(state, request.user).get()

        try:
            await OneTimePassword.validate_user(state, user, otp)
        except InvalidAccountAuth:
            raise

        otp_secret = pyotp.random_base32()

        await state.mongo.user.update_one(
            {"_id": request.user},
            {"$set": {"otp.completed": False, "otp.secret": otp_secret}},
        )

        return OtpModel(secret=otp_secret, completed=False)


@delete(
    path="/logout",
    description="Logout of User account",
    tags=["account"],
    status_code=200,
)
async def logout() -> Response:
    response = Response(content=None)
    response.delete_cookie(jwt_cookie_auth.key)
    return response


router = Router(
    path="/account",
    route_handlers=[LoginController, OtpController, create_account, me, logout],
)

import secrets
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Optional

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
from app.models.user import (
    CreateUserModel,
    PublicUserModel,
    UserLoginSignatureModel,
    UserModel,
    UserToSignModel,
)
from bson import ObjectId
from lib.mCaptcha import validate_captcha
from litestar import Response, Router, delete
from litestar.controller import Controller
from litestar.exceptions import ValidationException
from litestar.handlers import get, post
from nacl.encoding import Base64Encoder
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

if TYPE_CHECKING:
    from app.types import State


class LoginController(Controller):
    path = "/{email:str}"

    @get(path="/public", description="Public KDF details", tags=["account"])
    async def public(self, state: "State", email: str) -> PublicUserModel:
        user = await User(state, email).get()

        return PublicUserModel(kdf=user.kdf, otp_completed=user.otp.completed)

    @post(
        path="/setup/otp",
        description="Used to confirm OTP is completed",
        tags=["account"],
        status_code=201,
        raises=[OtpAlreadyCompleted],
    )
    async def otp_setup(self, state: "State", email: str, otp: str) -> Response:
        user = await User(state, email).get()

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

    @get(
        path="/to-sign",
        description="Used to generate a unique code to sign.",
        tags=["account"],
        raises=[UserNotFoundException],
    )
    async def to_sign(self, state: "State", email: str) -> UserToSignModel:
        try:
            user = await User(state, email).get()
        except UserNotFoundException:
            raise
        else:
            to_sign = secrets.token_urlsafe(64)
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
    )
    async def login(
        self,
        state: "State",
        captcha: str,
        otp: Optional[str],
        data: UserLoginSignatureModel,
        email: str,
    ) -> Response[UserModel]:
        try:
            await validate_captcha(state, captcha)
        except InvalidCaptcha:
            raise

        user = await User(state, email).get()

        if user.otp.completed:
            try:
                await OneTimePassword.validate_user(state, user, otp)
            except InvalidAccountAuth:
                raise

        proof_search = {"user_id": ObjectId(user.id), "_id": ObjectId(data.id)}
        proof = await state.mongo.proof.find_one(proof_search)
        if not proof:
            raise InvalidAccountAuth()

        await state.mongo.proof.delete_one(proof_search)

        try:
            public_key = Base64Encoder.decode(user.ed25199.public_key.encode())
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

        return jwt_cookie_auth.login(
            identifier=str(user.id),
            token_expiration=timedelta(days=1),
            response_body=user,
            token_unique_jwt_id=secrets.token_urlsafe(32),
        )

    @delete(
        path="/logout",
        description="Logout of User account",
        tags=["account"],
        status_code=200,
    )
    async def logout(self) -> Response:
        response = Response(content=None)
        response.delete_cookie(jwt_cookie_auth.key)
        return response


@post(
    path="/create",
    description="Create a user account",
    tags=["account"],
    status_code=201,
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
        {**data.dict(), "otp": {"secret": pyotp.random_base32(), "completed": False}}
    )

    return Response(None, status_code=201)


router = Router(path="/account", route_handlers=[LoginController, create_account])

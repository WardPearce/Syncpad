import secrets
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Optional

from app.errors import (
    EmailTaken,
    InvalidAccountAuth,
    InvalidCaptcha,
    UserNotFoundException,
)
from app.lib.jwt import jwt_cookie_auth
from app.lib.otp import OneTimePassword
from app.lib.user import User
from app.models.user import (
    Argon2Modal,
    CreateUserModel,
    UserLoginSignatureModel,
    UserModel,
    UserToSignModel,
)
from bson import ObjectId
from lib.mCaptcha import validate_captcha
from litestar import Response, Router
from litestar.controller import Controller
from litestar.handlers import get, post
from nacl.encoding import Base64Encoder
from nacl.exceptions import BadSignatureError
from nacl.signing import VerifyKey

if TYPE_CHECKING:
    from app.types import State


class LoginController(Controller):
    path = "/{email:str}"

    @get(path="/kdf", description="Public KDF details", tags=["account"])
    async def kdf(self, state: "State", email: str) -> Argon2Modal:
        return (await User(state, email).get()).kdf

    @get(
        path="/to-sign",
        description="Used to generate a unique code to sign.",
        tags=["account"],
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
                    "user_id": user.id,
                    "expires": datetime.now(tz=timezone.utc) + timedelta(seconds=60),
                }
            )
            return UserToSignModel(to_sign=to_sign, _id=result.inserted_id)

    @post(
        path="/login", description="Validate signature and OTP code", tags=["account"]
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

        try:
            await OneTimePassword.validate_user(state, user, otp)
        except InvalidAccountAuth:
            raise

        proof_search = {"user_id": user.id, "_id": ObjectId(data.id)}
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


@post(path="/create", tags=["account"])
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

    result = await state.mongo.user.insert_one(data.dict())

    return jwt_cookie_auth.login(
        identifier=str(result.inserted_id),
        token_expiration=timedelta(days=1),
        token_unique_jwt_id=secrets.token_urlsafe(32),
    )


router = Router(path="/account", route_handlers=[LoginController, create_account])

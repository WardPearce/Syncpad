import secrets
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, Optional

import pyotp
from bson import ObjectId
from bson.errors import InvalidId
from litestar import Request, Response, Router, delete
from litestar.background_tasks import BackgroundTask
from litestar.contrib.jwt import Token
from litestar.controller import Controller
from litestar.exceptions import NotAuthorizedException, ValidationException
from litestar.handlers import get, post
from litestar.response import Redirect
from nacl.encoding import Base64Encoder
from nacl.exceptions import BadSignatureError
from nacl.public import PublicKey, SealedBox
from nacl.signing import VerifyKey

from app.env import SETTINGS
from app.errors import (
    EmailTaken,
    InvalidAccountAuth,
    InvalidCaptcha,
    OtpAlreadyCompleted,
    TooManyWebhooks,
    UserNotFoundException,
)
from app.lib.geoip import GeoIp
from app.lib.jwt import delete_all_user_sessions, delete_session, jwt_cookie_auth
from app.lib.mCaptcha import validate_captcha
from app.lib.otp import OneTimePassword
from app.lib.smtp import send_email_verify
from app.lib.user import User, generate_email_validation
from app.models.jwt import UserJtiModel
from app.models.session import CreateSessionModel, SessionLocationModel
from app.models.user import (
    AccountUpdatePassword,
    CreateUserModel,
    NotificationEnum,
    OtpModel,
    PublicUserModel,
    UserLoginSignatureModel,
    UserModel,
    UserToSignModel,
    WebhookModel,
)

if TYPE_CHECKING:
    from app.custom_types import State


class LoginController(Controller):
    path = "/{email:str}"

    @get(
        path="/public",
        description="Public KDF details",
        tags=["account"],
        exclude_from_auth=True,
        cache=120,
    )
    async def public(self, state: "State", email: str) -> PublicUserModel:
        user = await User(state, email).get()

        return PublicUserModel(kdf=user.kdf, otp_completed=user.otp.completed)

    @get(
        "/email/verify/{email_secret:str}",
        description="Verify email for given account",
        tags=["account"],
        exclude_from_auth=True,
    )
    async def verify_email(
        self, state: "State", email: str, email_secret: str
    ) -> Redirect:
        user = await User(state, email).get()

        email_search = {"email": user.email, "secret": email_secret}

        if (
            not user.email_verified
            and await state.mongo.email_verification.count_documents(email_search) > 0
        ):
            await state.mongo.user.update_one(
                {"email": email},
                {"$set": {"email_verified": True}},
            )

            await state.mongo.email_verification.delete_one(email_search)

            return Redirect(SETTINGS.proxy_urls.frontend + "/email-verified")

        return Redirect(SETTINGS.proxy_urls.frontend)

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
                    "expires": datetime.utcnow() + timedelta(minutes=4),
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

        try:
            proof_search = {"user_id": ObjectId(user.id), "_id": ObjectId(data.id)}
        except InvalidId:
            raise InvalidAccountAuth()

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

        now = datetime.utcnow()
        token_timedelta = (
            timedelta(days=SETTINGS.jwt.expire_days)
            if not data.one_day_login
            else timedelta(days=1)
        )

        location = SessionLocationModel()
        device: Optional[str] = None

        try:
            sealed_box = SealedBox(
                PublicKey(Base64Encoder.decode(user.keypair.public_key.encode()))
            )
        except ValueError:
            pass
        else:

            def __base64_public_encrypt(data: str) -> str:
                return Base64Encoder.encode(sealed_box.encrypt(data.encode())).decode()

            if (
                user.ip_lookup_consent
                and SETTINGS.proxy_check
                and request.client
                and request.client.host
            ):
                client_ip = request.client.host
                geoip_lookup = await GeoIp(state, client_ip).get()

                if geoip_lookup:
                    location = SessionLocationModel(
                        region=__base64_public_encrypt(
                            geoip_lookup.get("region", "Unknown")
                        ),
                        country=__base64_public_encrypt(
                            geoip_lookup.get("country", "Unknown")
                        ),
                        ip=__base64_public_encrypt(client_ip),
                    )

            if "User-Agent" in request.headers:
                device = __base64_public_encrypt(request.headers["User-Agent"])

        session = await state.mongo.session.insert_one(
            CreateSessionModel(
                expires=now + token_timedelta,
                record_kept_till=now + timedelta(days=SETTINGS.jwt.expire_days * 3),
                created=now,
                location=location,
                device=device,
                user_id=user.id,
            ).dict()
        )

        # If OTP mark as completed, redact secrets.
        if user.otp.completed:
            user.otp.secret = None
            user.otp.provisioning_uri = None

        return jwt_cookie_auth.login(
            identifier=str(user.id),
            token_expiration=token_timedelta,
            response_body=UserJtiModel(jti=session.inserted_id, user=user),
            token_unique_jwt_id=str(session.inserted_id),
        )


@post(
    "/email/resend",
    description="Resends email verification",
    tags=["account"],
)
async def email_resend(state: "State", request: Request[ObjectId, Token, Any]) -> None:
    user = await User(state, request.user).get()
    if not user.email_verified:
        email_verification = await state.mongo.email_verification.find_one(
            {"email": user.email}
        )
        if email_verification:
            email_secret = email_verification["secret"]
        else:
            # If no validation code, create a new one.
            email_secret = await generate_email_validation(state, user.email)

        await send_email_verify(to=user.email, email_secret=email_secret)


@post(
    "/password/reset",
    description="Reset password",
    tags=["account"],
)
async def password_reset(
    state: "State",
    request: Request[ObjectId, Token, Any],
    data: AccountUpdatePassword,
    otp: Optional[str],
) -> None:
    user = await User(state, request.user).get()

    try:
        await OneTimePassword.validate_user(state, user, otp)
    except InvalidAccountAuth:
        raise

    await state.mongo.user.update_one(
        {"_id": user.id},
        {"$set": data.dict()},
    )

    await delete_all_user_sessions(state, request.user)


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
    if SETTINGS.disable_registration:
        raise NotAuthorizedException(detail="Registration is disabled")

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
            "email": email,
            "email_verified": False,
            "created": datetime.utcnow(),
            "otp": {"secret": pyotp.random_base32(), "completed": False},
            "notifications": {
                "email": [
                    NotificationEnum.canary_renewals.value,
                    NotificationEnum.canary_subscriptions.value,
                    NotificationEnum.survey_submissions.value,
                ],
                "webhooks": {},
            },
        }
    )

    return Response(
        None,
        status_code=201,
        background=BackgroundTask(
            send_email_verify,
            to=data.email,
            email_secret=await generate_email_validation(state, email),
        ),
    )


@get(path="/me", description="Get user info", tags=["account"])
async def get_me(state: "State", request: Request[ObjectId, Token, Any]) -> UserModel:
    return await User(state, request.user).get(redact_otp=True)


@get(
    path="/jwt",
    description="Get JWT sub for user",
    tags=["account"],
    sync_to_thread=False,
)
def jwt_info(request: Request[ObjectId, Token, Any]) -> str:
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

        await delete_all_user_sessions(state, request.user)

        return OtpModel(secret=otp_secret, completed=False)


class EmailNotificationController(Controller):
    path = "/notifications/email"

    @post(
        "/add",
        description="Enable email notification",
        tags=["account", "notifications"],
    )
    async def add_email(
        self,
        state: "State",
        request: Request[ObjectId, Token, Any],
        data: NotificationEnum,
    ) -> None:
        await state.mongo.user.update_one(
            {"_id": request.user}, {"$push": {"notifications.email": data.value}}
        )

    @delete(
        "/remove",
        description="Disable email notification",
        tags=["account", "notifications"],
    )
    async def remove_email(
        self,
        state: "State",
        request: Request[ObjectId, Token, Any],
        data: NotificationEnum,
    ) -> None:
        await state.mongo.user.update_one(
            {"_id": request.user}, {"$pull": {"notifications.email": data.value}}
        )


class WebhookController(Controller):
    path = "/notifications/webhook"

    @delete(
        "/remove",
        description="Remove a webhook",
        tags=["account", "notifications", "webhook"],
    )
    async def remove_webhook(
        self,
        state: "State",
        request: Request[ObjectId, Token, Any],
        data: WebhookModel,
    ) -> None:
        await state.mongo.user.update_one(
            {"_id": request.user},
            {"$pull": {f"notifications.webhooks.{data.type.value}": data.url}},
        )

    @post(
        "/add",
        description="Add a webhook",
        tags=["account", "notifications", "webhook"],
    )
    async def add_webhook(
        self,
        state: "State",
        request: Request[ObjectId, Token, Any],
        data: WebhookModel,
    ) -> None:
        user = await User(state, request.user).get()
        if (
            data.type in user.notifications.webhooks
            and len(user.notifications.webhooks[data.type]) >= 3
        ):
            raise TooManyWebhooks()

        await state.mongo.user.update_one(
            {
                "_id": request.user,
                f"notifications.webhooks.{data.type.value}": {"$exists": False},
            },
            {
                "$set": {"notifications.webhooks": {data.type.value: []}},
            },
        )

        await state.mongo.user.update_one(
            {"_id": request.user},
            {
                "$push": {f"notifications.webhooks.{data.type.value}": data.url},
            },
        )


class PrivacyController(Controller):
    path = "/privacy"

    @delete(
        "/ip-progressing/disallow",
        tags=["account", "privacy"],
    )
    async def ip_progressing(
        self,
        state: "State",
        request: Request[ObjectId, Token, Any],
    ) -> None:
        await state.mongo.user.update_one(
            {"_id": request.user},
            {"$set": {"ip_lookup_consent": False}},
        )

    @post(
        "/ip-progressing/consent",
        tags=["account", "privacy"],
    )
    async def ip_progressing_consent(
        self,
        state: "State",
        request: Request[ObjectId, Token, Any],
    ) -> None:
        await state.mongo.user.update_one(
            {"_id": request.user},
            {"$set": {"ip_lookup_consent": True}},
        )


@delete(
    path="/logout",
    description="Logout of User account",
    tags=["account"],
    status_code=200,
)
async def logout(request: Request[ObjectId, Token, Any], state: "State") -> Response:
    response = Response(content=None)
    response.delete_cookie(jwt_cookie_auth.key)

    # Invalidate session.
    await delete_session(state, ObjectId(request.auth.jti), request.user)

    return response


router = Router(
    path="/account",
    route_handlers=[
        LoginController,
        OtpController,
        WebhookController,
        EmailNotificationController,
        PrivacyController,
        create_account,
        jwt_info,
        email_resend,
        logout,
        get_me,
        password_reset,
    ],
)

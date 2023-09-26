import base64
import binascii
from datetime import datetime, timedelta
from typing import TYPE_CHECKING, Any, AsyncGenerator, List, Optional

import argon2
from argon2 import PasswordHasher
from bson import ObjectId
from bson.errors import InvalidId
from cryptography.hazmat.primitives import hashes, hmac
from litestar import Request, Response, Router, WebSocket, websocket
from litestar.background_tasks import BackgroundTask
from litestar.channels import ChannelsPlugin
from litestar.contrib.jwt import Token
from litestar.controller import Controller
from litestar.exceptions import NotAuthorizedException
from litestar.handlers import get, post
from litestar.response import Stream

from app.errors import (
    InvalidAccountAuth,
    SurveyAlreadySubmittedException,
    SurveyKeyInvalidException,
    SurveyNotFoundException,
    SurveyProxyBlockException,
    SurveyRequiredQuestionsNotAnswered,
)
from app.lib.geoip import GeoIp
from app.lib.jwt import jwt_cookie_auth
from app.lib.key_bulders import logged_in_user_key_builder
from app.lib.mCaptcha import validate_captcha
from app.lib.survey import Survey, SurveyUser

if TYPE_CHECKING:
    from app.custom_types import State

from app.models.survey import (
    SubmitSurveyModel,
    SurveyCreateModel,
    SurveyModel,
    SurveyPublicModel,
    SurveyResultModel,
)


@post(
    "/create",
    description="Create a survey",
)
async def create_survey(
    request: Request[ObjectId, Token, Any], data: SurveyCreateModel, state: "State"
) -> SurveyModel:
    insert = {
        **data.model_dump(),
        "created": datetime.utcnow(),
        "user_id": request.user,
    }

    if data.ip:
        try:
            raw_ip_key = base64.b64decode(data.ip.key)
        except (ValueError, binascii.Error):
            raise SurveyKeyInvalidException()

        if len(raw_ip_key) != 32:
            raise SurveyKeyInvalidException()

        insert["ip"]["key"] = PasswordHasher().hash(data.ip.key)

    await state.mongo.survey.insert_one(insert)
    return SurveyModel(**insert)


@get(
    "/list",
    description="List surveys",
    cache_key_builder=logged_in_user_key_builder,
)
async def list_surveys(
    request: Request[None, Token, Any], state: "State"
) -> List[SurveyModel]:
    surveys: List[SurveyModel] = []
    async for survey in state.mongo.survey.find({"user_id": request.user}):
        surveys.append(SurveyModel(**survey))
    return surveys


class SurveyController(Controller):
    path = "/{survey_id:str}"

    @websocket(
        "/responses/realtime",
        description="Stream survey responses in realtime",
    )
    async def stream_responses_ws(
        self,
        socket: WebSocket,
        channels: ChannelsPlugin,
        state: "State",
        survey_id: str,
        pull_history: str = "true",
    ) -> None:
        try:
            id_ = ObjectId(survey_id)
        except InvalidId:
            await socket.close()
            raise SurveyNotFoundException()

        user = Survey(state, id_).user(socket.user)

        try:
            await user.exists()
        except SurveyNotFoundException:
            await socket.close()
            return

        await socket.accept()

        async with channels.start_subscription(
            [f"survey.results.{survey_id}"]
        ) as subscriber:
            if pull_history.lower() == "true":
                async for answer in user.answers():
                    await socket.send_json(answer.json(by_alias=True))

            async for message in subscriber.iter_events():
                await socket.send_json(message.decode())

    async def __stream_responses(
        self, survey: SurveyUser
    ) -> AsyncGenerator[bytes, None]:
        async for answer in survey.answers():
            yield (answer.json(by_alias=True) + "\n").encode()

    @get(
        "/responses", description="Stream survey responses using ndjson (not realtime)"
    )
    async def stream_responses(
        self,
        state: "State",
        request: Request[ObjectId, Token, Any],
        survey_id: str,
    ) -> Stream:
        try:
            id_ = ObjectId(survey_id)
        except InvalidId:
            raise SurveyNotFoundException()

        survey = Survey(state, id_).user(request.user)

        return Stream(self.__stream_responses(survey))

    @get("/responses/{page:int}", description="Get a survey response")
    async def get_response(
        self,
        state: "State",
        request: Request[ObjectId, Token, Any],
        survey_id: str,
        page: int,
    ) -> SurveyResultModel:
        try:
            id_ = ObjectId(survey_id)
        except InvalidId:
            raise SurveyNotFoundException()

        survey = Survey(state, id_).user(request.user)

        return await survey.answer(page)

    @post("/close", description="Closes survey submission, also clears IP hashes")
    async def close_survey(
        self, state: "State", request: Request[ObjectId, Token, Any], survey_id: str
    ) -> None:
        try:
            id_ = ObjectId(survey_id)
        except InvalidId:
            raise SurveyNotFoundException()

        await Survey(state, id_).user(request.user).close()

    @post("/submit", description="Submit answers to a survey", exclude_from_auth=True)
    async def submit_survey(
        self,
        state: "State",
        request: Request[None, Token, Any],
        channels: ChannelsPlugin,
        survey_id: str,
        data: SubmitSurveyModel,
        captcha: Optional[str] = None,
    ) -> Response:
        try:
            id_ = ObjectId(survey_id)
        except InvalidId:
            raise SurveyNotFoundException()

        survey = await Survey(state, id_).get()

        provided_question_ids = [q.id for q in data.answers]
        valid_question_ids = []
        for question in survey.questions:
            if question.required and question.id not in provided_question_ids:
                raise SurveyRequiredQuestionsNotAnswered()

            valid_question_ids.append(question.id)

        if not all(
            [question_id in valid_question_ids for question_id in provided_question_ids]
        ):
            raise SurveyRequiredQuestionsNotAnswered()

        ip_expires = datetime.utcnow() + timedelta(days=7)
        if isinstance(survey.closed, datetime):
            if datetime.utcnow() > survey.closed:
                raise SurveyNotFoundException()

            ip_expires = survey.closed
        elif survey.closed:
            raise SurveyNotFoundException()

        if survey.requires_captcha:
            await validate_captcha(state, captcha)

        user_id = None
        if jwt_cookie_auth.key in request.cookies:
            try:
                decoded = Token.decode(
                    request.cookies[jwt_cookie_auth.key].replace("Bearer ", ""),
                    jwt_cookie_auth.token_secret,
                    jwt_cookie_auth.algorithm,
                )
                user_id = ObjectId(decoded.sub)
            except NotAuthorizedException:
                if survey.requires_login:
                    raise InvalidAccountAuth()

        elif survey.requires_login:
            raise InvalidAccountAuth()

        response = Response(None)

        if not survey.allow_multiple_submissions:
            if request.cookies.get(survey_id) is not None:
                raise SurveyAlreadySubmittedException()

            response.set_cookie(
                survey_id, "true", max_age=2074000, path=f"/api{request.url.path}"
            )

            if (
                user_id
                and await state.mongo.survey.count_documents(
                    {"survey_id": id_, "user_id": user_id}
                )
                > 0
            ):
                raise SurveyAlreadySubmittedException()

            if request.client and request.client.host and survey.ip:
                if not data.ip_key:
                    raise SurveyKeyInvalidException()

                try:
                    PasswordHasher().verify(survey.ip.key, data.ip_key)
                except (
                    argon2.exceptions.VerificationError,
                    argon2.exceptions.VerifyMismatchError,
                ):
                    raise SurveyKeyInvalidException()

                try:
                    raw_ip_key = base64.b64decode(data.ip_key)
                except (ValueError, binascii.Error):
                    raise SurveyKeyInvalidException()

                ip_hmac = hmac.HMAC(raw_ip_key, hashes.SHA256())
                ip_hmac.update(request.client.host.encode())

                ip_hash = base64.b64encode(ip_hmac.finalize()).decode()

                if (
                    await state.mongo.survey_blocker.count_documents(
                        {
                            "survey_id": id_,
                            "ip_hash": ip_hash,
                        }
                    )
                    > 0
                ):
                    raise SurveyAlreadySubmittedException()

                await state.mongo.survey_blocker.insert_one(
                    {
                        "survey_id": id_,
                        "ip_hash": ip_hash,
                        "expires": ip_expires,
                    }
                )

        if survey.proxy_block and request.client and request.client.host:
            geoip_lookup = await GeoIp(state, request.client.host).get()
            if geoip_lookup and geoip_lookup["proxy"] == "yes":
                raise SurveyProxyBlockException()

        inserted = await Survey(state, id_).submit(data, user_id=user_id)

        channels.publish(
            inserted.model_dump_json(by_alias=True), f"survey.results.{survey_id}"
        )

        response.background = BackgroundTask(
            Survey(state, id_).alert_subscribed, submission=inserted.model_dump()
        )

        return response

    @get("/", description="Get a survey")
    async def get_survey(
        self,
        state: "State",
        request: Request[ObjectId, Token, Any],
        survey_id: str,
    ) -> SurveyModel:
        try:
            id_ = ObjectId(survey_id)
        except InvalidId:
            raise SurveyNotFoundException()

        return await Survey(state, id_).user(request.user).get()

    @get("/public", description="Get a survey public details", exclude_from_auth=True)
    async def public_survey(
        self,
        state: "State",
        survey_id: str,
    ) -> SurveyPublicModel:
        try:
            id_ = ObjectId(survey_id)
        except InvalidId:
            raise SurveyNotFoundException()

        survey = await Survey(state, id_).public()

        if isinstance(survey.closed, bool):
            if survey.closed:
                raise SurveyNotFoundException()
        elif datetime.utcnow() > survey.closed:
            raise SurveyNotFoundException()

        return survey


router = Router(
    path="/survey",
    tags=["survey"],
    route_handlers=[SurveyController, create_survey, list_surveys],
)

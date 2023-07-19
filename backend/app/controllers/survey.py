import hashlib
from datetime import date, datetime, timedelta
from secrets import token_urlsafe
from typing import TYPE_CHECKING, Any, AsyncGenerator, List, Optional

from bson import ObjectId
from bson.errors import InvalidId
from litestar import Request, Response, Router
from litestar.contrib.jwt import Token
from litestar.controller import Controller
from litestar.exceptions import NotAuthorizedException
from litestar.handlers import get, post
from litestar.middleware.rate_limit import RateLimitConfig
from litestar.response import Stream

from app.errors import (
    InvalidAccountAuth,
    SurveyAlreadySubmittedException,
    SurveyNotFoundException,
    SurveyProxyBlockException,
    SurveyRequiredQuestionsNotAnswered,
)
from app.lib.geoip import GeoIp
from app.lib.jwt import jwt_cookie_auth
from app.lib.key_bulders import logged_in_user_key_builder
from app.lib.mCaptcha import validate_captcha
from app.lib.survey import Survey

if TYPE_CHECKING:
    from app.custom_types import State

from app.models.survey import (
    SubmitSurveyModel,
    SurveyCreateModel,
    SurveyModel,
    SurveyPublicModel,
)


@post(
    "/create",
    description="Create a survey",
    middleware=[RateLimitConfig(rate_limit=("minute", 3)).middleware],
)
async def create_survey(
    request: Request[ObjectId, Token, Any], data: SurveyCreateModel, state: "State"
) -> SurveyModel:
    insert = {**data.dict(), "created": datetime.utcnow(), "user_id": request.user}
    if not data.allow_multiple_submissions:
        insert["ip_salt"] = token_urlsafe(16)

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

    @get("/responses/stream", description="Stream survey responses")
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

        survey = Survey(state, id_)

        await survey.user(request.user).exists()

        async def stream() -> AsyncGenerator[bytes, None]:
            async for answer in survey.stream_answers():
                yield (answer.json(by_alias=True) + "\n").encode()

        return Stream(stream)

    @post("/submit", description="Submit answers to a survey", exclude_from_auth=True)
    async def submit_survey(
        self,
        state: "State",
        request: Request[Optional[ObjectId], Token, Any],
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

        if isinstance(survey.closed, bool):
            if survey.closed:
                raise SurveyNotFoundException()
        elif datetime.utcnow() > survey.closed:
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

            response.set_cookie(survey_id, "true")

            if (
                user_id
                and await state.mongo.survey.count_documents(
                    {"survey_id": id_, "user_id": user_id}
                )
                > 0
            ):
                raise SurveyAlreadySubmittedException()

            if request.client and request.client.host and survey.ip_salt:
                ip_hash = hashlib.sha256(
                    (request.client.host + survey.ip_salt).encode()
                ).hexdigest()

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
                        "expires": datetime.utcnow() + timedelta(hours=24),
                    }
                )

        if survey.proxy_block and request.client and request.client.host:
            geoip_lookup = await GeoIp(state, request.client.host).get()
            if geoip_lookup and geoip_lookup["proxy"] == "yes":
                raise SurveyProxyBlockException()

        await Survey(state, id_).submit(data, user_id=user_id)

        return response

    @get("/public", description="Get a survey", exclude_from_auth=True)
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

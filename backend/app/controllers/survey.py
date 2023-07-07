from datetime import datetime
from typing import TYPE_CHECKING, Any, Optional

from bson import ObjectId
from bson.errors import InvalidId
from litestar import Controller, Request, Router, get, post
from litestar.contrib.jwt import Token

from app.errors import InvalidAccountAuth, SurveyNotFoundException

if TYPE_CHECKING:
    from app.custom_types import State

from app.models.survey import SurveyCreateModel, SurveyModel, SurveyPublicModel


@post("/create", description="Create a survey")
async def create_survey(
    request: Request[ObjectId, Token, Any], data: SurveyCreateModel, state: "State"
) -> SurveyModel:
    insert = {**data.dict(), "created": datetime.utcnow(), "user_id": request.user}
    await state.mongo.survey.insert_one(insert)
    return SurveyModel(**insert)


class SurveyController(Controller):
    path = "/{survey_id:str}"

    @get(
        "/",
        description="Get a survey",
        exclude_from_auth=True,
    )
    async def get(
        self,
        request: Request[Optional[ObjectId], Token, Any],
        state: "State",
        survey_id: str,
    ) -> SurveyPublicModel:
        try:
            id_ = ObjectId(survey_id)
        except InvalidId:
            raise SurveyNotFoundException()

        survey = await state.mongo.survey.find_one({"_id": id_})
        if not survey:
            raise SurveyNotFoundException()

        survey = SurveyPublicModel(**survey)

        if survey.requires_login and not request.user:
            raise InvalidAccountAuth()

        return survey


router = Router(
    path="/survey",
    tags=["survey"],
    route_handlers=[create_survey, SurveyController],
)

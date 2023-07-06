from datetime import datetime
from typing import TYPE_CHECKING, Any

from bson import ObjectId
from litestar import Request, Router, post
from litestar.contrib.jwt import Token

if TYPE_CHECKING:
    from app.custom_types import State

from app.models.survey import SurveyCreateModel, SurveyModel


@post("/create", description="Create a survey")
async def create_survey(
    request: Request[ObjectId, Token, Any], data: SurveyCreateModel, state: "State"
) -> SurveyModel:
    insert = {**data.dict(), "created": datetime.utcnow(), "user_id": request.user}
    await state.mongo.survey.insert_one(insert)
    return SurveyModel(**insert)


router = Router(
    path="/survey",
    tags=["survey"],
    route_handlers=[create_survey],
)

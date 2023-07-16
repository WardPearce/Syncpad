from datetime import datetime
from typing import TYPE_CHECKING, Any, Mapping, Optional

from bson import ObjectId

from app.errors import SurveyNotFoundException
from app.models.survey import SubmitSurveyModel, SurveyModel, SurveyPublicModel

if TYPE_CHECKING:
    from app.custom_types import State


class Survey:
    def __init__(self, state: "State", survey_id: ObjectId) -> None:
        self._state = state
        self._survey_id = survey_id

    async def __get_raw(self) -> Mapping[str, Any]:
        survey = await self._state.mongo.survey.find_one({"_id": self._survey_id})
        if not survey:
            raise SurveyNotFoundException()

        return survey

    async def get(self) -> SurveyModel:
        return SurveyModel(**(await self.__get_raw()))

    async def public(self) -> SurveyPublicModel:
        return SurveyPublicModel(**(await self.__get_raw()))

    async def submit_answers(
        self, answers: SubmitSurveyModel, user_id: Optional[ObjectId] = None
    ) -> None:
        await self._state.mongo.survey_answer.insert_one(
            {
                **answers.dict(),
                "survey_id": self._survey_id,
                "created": datetime.utcnow(),
                "user_id": user_id,
            }
        )

import asyncio
from datetime import datetime
from typing import TYPE_CHECKING, Any, AsyncGenerator, Mapping, Optional

from bson import ObjectId
from lib.ntfy import push_notification
from lib.smtp import send_email
from lib.url import untrusted_http_request
from lib.user import User
from models.user import NotificationEnum

from app.errors import SurveyNotFoundException, SurveyResultNotFoundException
from app.models.survey import (
    SubmitSurveyModel,
    SurveyModel,
    SurveyPublicModel,
    SurveyResultModel,
)

if TYPE_CHECKING:
    from app.custom_types import State


class SurveyUser:
    def __init__(self, upper: "Survey", user_id: ObjectId) -> None:
        self._upper = upper
        self._user_id = user_id

    @property
    def __query(self) -> Mapping[str, Any]:
        return {"_id": self._upper._survey_id, "user_id": self._user_id}

    async def __get_raw(self) -> Mapping[str, Any]:
        survey = await self._upper._state.mongo.survey.find_one(self.__query)
        if not survey:
            raise SurveyNotFoundException()

        return survey

    async def close(self) -> None:
        update = await self._upper._state.mongo.update_one(
            self.__query, {"closed": True}
        )

        if update.matched_count > 0:
            # Delete any hashed IPs for this survey.
            await self._upper._state.mongo.delete_many(
                {"survey_id": self._upper._survey_id}
            )

    async def answer(self, page: int) -> SurveyResultModel:
        result = await self._upper._state.mongo.survey_answer.find_one(
            {"survey_id": self._upper._survey_id, "user_id": self._user_id},
            sort=[("created", -1)],
            skip=page,
        )

        if not result:
            raise SurveyResultNotFoundException()

        return SurveyResultModel(**result)

    async def answers(self) -> AsyncGenerator[SurveyResultModel, None]:
        await self.exists()

        async for answer in self._upper._state.mongo.survey_answer.find(
            {"survey_id": self._upper._survey_id}
        ):
            yield SurveyResultModel(**answer)

    async def get(self) -> SurveyModel:
        return SurveyModel(**(await self.__get_raw()))

    async def exists(self) -> None:
        if await self._upper._state.mongo.survey.count_documents(self.__query) == 0:
            raise SurveyNotFoundException()


class Survey:
    def __init__(self, state: "State", survey_id: ObjectId) -> None:
        self._state = state
        self._survey_id = survey_id

    def user(self, user_id: ObjectId) -> SurveyUser:
        return SurveyUser(self, user_id)

    async def __get_raw(self) -> Mapping[str, Any]:
        survey = await self._state.mongo.survey.find_one({"_id": self._survey_id})
        if not survey:
            raise SurveyNotFoundException()

        return survey

    async def alert_subscribed(self, submission: dict) -> None:
        survey = await self.get()

        user = await User(self._state, survey.user_id).get()

        futures = []

        subject = "A new user has submitted a survey"
        message = "A new survey response has been submitted"

        if any(
            NotificationEnum.survey_submissions.value == enum.value
            for enum in user.notifications.email
        ):
            futures.append(
                send_email(
                    user.email,
                    subject,
                    message,
                )
            )

        if any(
            NotificationEnum.survey_submissions.value == enum.value
            for enum in user.notifications.push
        ):
            futures.append(
                push_notification(
                    self._state,
                    topic=user.notifications.push[NotificationEnum.survey_submissions],
                    message=message,
                    title=subject,
                    tags="mailbox_with_mail",
                    priority="high",
                )
            )

        if any(
            NotificationEnum.survey_submissions.value == enum.value
            for enum in user.notifications.webhooks
        ):
            for webhook in user.notifications.webhooks[
                NotificationEnum.survey_submissions
            ]:
                futures.append(
                    untrusted_http_request(
                        state=self._state, url=webhook, method="POST", json=submission
                    )
                )

        if futures:
            asyncio.gather(*futures)

    async def get(self) -> SurveyModel:
        return SurveyModel(**(await self.__get_raw()))

    async def public(self) -> SurveyPublicModel:
        return SurveyPublicModel(**(await self.__get_raw()))

    async def submit(
        self, answers: SubmitSurveyModel, user_id: Optional[ObjectId] = None
    ) -> SurveyResultModel:
        await self._state.mongo.survey.update_one(
            {"_id": self._survey_id}, {"$inc": {"responses_count": 1}}, upsert=True
        )

        insert = {
            **answers.model_dump(),
            "survey_id": self._survey_id,
            "created": datetime.utcnow(),
            "user_id": user_id,
        }
        await self._state.mongo.survey_answer.insert_one(insert)

        return SurveyResultModel(**insert)

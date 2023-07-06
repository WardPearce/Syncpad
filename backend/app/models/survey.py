from datetime import datetime
from enum import Enum
from typing import List, Literal, Optional, Union

from bson import ObjectId
from pydantic import BaseModel, Field

from app.models.customs import CustomJsonEncoder, IvField


class RegexModel(IvField):
    cipher_text: str = Field(
        ...,
        max_length=128,
    )


class DescriptionModel(IvField):
    cipher_text: str = Field(
        ...,
        max_length=1024,
    )


class ChoicesModel(IvField):
    cipher_text: str = Field(
        ...,
        max_length=512,
    )


class QuestionModel(IvField):
    cipher_text: str = Field(
        ...,
        max_length=256,
    )


class SurveyQuestionModel(BaseModel):
    id: int
    regex: Optional[RegexModel] = None
    description: Optional[DescriptionModel] = None
    question: Optional[QuestionModel] = None
    choices: Optional[List[ChoicesModel]] = Field(None, max_items=56)
    required: bool = False
    type: Union[
        Literal["Short Answer"],
        Literal["Paragraph"],
        Literal["Multiple Choice"],
        Literal["Checkboxes"],
    ]


class TitleModel(IvField):
    cipher_text: str = Field(
        ...,
        max_length=128,
    )


class SurveyCreateModel(BaseModel):
    title: TitleModel
    description: Optional[DescriptionModel] = None
    questions: List[SurveyQuestionModel] = Field(..., max_items=128)
    signature: str = Field(..., max_length=128)
    requires_login: bool = False
    proxy_block: bool = False
    allow_multiple_submissions: bool = False


class SurveyModel(SurveyCreateModel, CustomJsonEncoder):
    created: datetime
    id: ObjectId = Field(..., alias="_id")
    user_id: ObjectId

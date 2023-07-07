from datetime import datetime
from enum import Enum
from typing import List, Literal, Optional, Union

from bson import ObjectId
from pydantic import BaseModel, Field

from app.models.customs import CustomJsonEncoder, IvField


class SecretKeyModel(IvField):
    cipher_text: str = Field(
        ...,
        max_length=240,
        description="Xchacha20 secret key, encrypted with keychain, base64 encoded",
    )


class SignPublicKeyModel(BaseModel):
    public_key: str = Field(
        ..., max_length=44, description="ed25519 public key, base64 encoded"
    )


class SignKeyPairModel(SignPublicKeyModel, IvField):
    cipher_text: str = Field(
        ...,
        max_length=240,
        description="ed25519 private key, encrypted with keychain, base64 encoded",
    )


class KeypairCipherModel(IvField):
    cipher_text: str = Field(
        ...,
        max_length=240,
    )


class PublicKeyModel(BaseModel):
    public_key: KeypairCipherModel


class KeypairModel(PublicKeyModel):
    private_key: KeypairCipherModel


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


class __SurveySharedModel(BaseModel):
    title: TitleModel
    description: Optional[DescriptionModel] = None
    questions: List[SurveyQuestionModel] = Field(..., max_items=128)
    signature: str = Field(..., max_length=128)
    requires_login: bool = False
    proxy_block: bool = False
    allow_multiple_submissions: bool = False


class SurveyCreateModel(__SurveySharedModel):
    sign_keypair: SignKeyPairModel
    secret_key: SecretKeyModel
    keypair: KeypairModel


class SurveyPublicModel(__SurveySharedModel, CustomJsonEncoder):
    created: datetime
    id: ObjectId = Field(..., alias="_id")
    user_id: ObjectId
    sign_keypair: SignPublicKeyModel
    keypair: PublicKeyModel


class SurveyModel(SurveyPublicModel):
    sign_keypair: SignKeyPairModel
    secret_key: SecretKeyModel
    keypair: KeypairModel

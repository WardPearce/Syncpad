from datetime import datetime
from enum import Enum
from typing import List, Literal, Optional, Union

from bson import ObjectId
from pydantic import BaseModel, Field

from app.models.customs import CustomJsonEncoder, IvField


class SurveySecretKeyModel(IvField):
    cipher_text: str = Field(
        ...,
        max_length=240,
        description="Xchacha20 secret key, encrypted with keychain, base64 encoded",
    )


class SurveySignPublicKeyModel(BaseModel):
    public_key: str = Field(
        ..., max_length=44, description="ed25519 public key, base64 encoded"
    )


class SurveySignKeyPairModel(SurveySignPublicKeyModel, IvField):
    cipher_text: str = Field(
        ...,
        max_length=240,
        description="ed25519 private key, encrypted with keychain, base64 encoded",
    )


class SurveyKeypairCipherModel(IvField):
    cipher_text: str = Field(
        ...,
        max_length=240,
    )


class SurveyPublicKeyModel(BaseModel):
    public_key: SurveyKeypairCipherModel


class SurveyKeypairModel(SurveyPublicKeyModel):
    private_key: SurveyKeypairCipherModel


class SurveyRegexModel(IvField):
    cipher_text: str = Field(
        ...,
        max_length=128,
    )


class SurveyDescriptionModel(IvField):
    cipher_text: str = Field(
        ...,
        max_length=1024,
    )


class SurveyChoicesModel(IvField):
    id: int
    cipher_text: str = Field(
        ...,
        max_length=512,
    )


class SurveyQuestionsModel(IvField):
    cipher_text: str = Field(
        ...,
        max_length=256,
    )


class SurveyQuestionModel(BaseModel):
    id: int
    regex: Optional[SurveyRegexModel] = None
    description: Optional[SurveyDescriptionModel] = None
    question: SurveyQuestionsModel
    choices: Optional[List[SurveyChoicesModel]] = Field(None, max_items=56)
    required: bool = False
    type: Union[
        Literal["Short Answer"],
        Literal["Paragraph"],
        Literal["Multiple Choice"],
        Literal["Single Choice"],
    ]


class TitleModel(IvField):
    cipher_text: str = Field(
        ...,
        max_length=128,
    )


class __SurveySharedModel(BaseModel):
    title: TitleModel
    description: Optional[SurveyDescriptionModel] = None
    questions: List[SurveyQuestionModel] = Field(..., max_items=128)
    signature: str = Field(..., max_length=128)
    requires_login: bool = False
    proxy_block: bool = False
    allow_multiple_submissions: bool = False
    algorithms: str = Field(
        "XChaCha20Poly1305+ED25519+X25519_XSalsa20Poly1305+BLAKE2b",
        description="Encryption algorithms used for survey",
    )


class SurveyCreateModel(__SurveySharedModel):
    sign_keypair: SurveySignKeyPairModel
    secret_key: SurveySecretKeyModel
    keypair: SurveyKeypairModel


class SurveyPublicModel(__SurveySharedModel, CustomJsonEncoder):
    created: datetime
    id: ObjectId = Field(..., alias="_id")
    user_id: ObjectId
    sign_keypair: SurveySignPublicKeyModel
    keypair: SurveyPublicKeyModel


class SurveyModel(SurveyPublicModel, SurveyCreateModel):
    pass

from datetime import datetime
from enum import Enum
from typing import Dict, Optional

from app.env import SETTINGS
from bson import ObjectId
from models.customs import CustomJsonEncoder, IvField
from pydantic import BaseModel, Field, validator


class DomainModel(BaseModel):
    domain: str = Field(
        ...,
        regex=r"(?i)^((?!(?:www|www\d+)\.)[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+(?:[a-zA-Z]{2,})$",
    )


class PublicKeyModel(BaseModel):
    public_key: str = Field(
        ..., max_length=44, description="ed25519 public key, base64 encoded"
    )


class CanaryEd25519Model(IvField, PublicKeyModel):
    cipher_text: str = Field(
        ...,
        max_length=240,
        description="ed25519 private key, encrypted with keychain, base64 encoded",
    )


class __CanarySharedModel(CustomJsonEncoder, DomainModel):
    about: str = Field(..., max_length=500)
    signature: str = Field(..., max_length=128)
    algorithms: str = Field(
        "XCHACHA20_POLY1305+ED25519+BLAKE2b",
        max_length=120,
        description="Algorithms used for canary",
    )


class CreateCanaryModel(__CanarySharedModel):
    keypair: CanaryEd25519Model


class PublicCanaryModel(__CanarySharedModel):
    id: ObjectId = Field(..., alias="_id")
    logo: Optional[str] = None
    user_id: ObjectId
    created: datetime
    keypair: PublicKeyModel

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        if self.logo:
            self.logo = f"{SETTINGS.s3.download_url}/canary/logos/{self.logo}"


class DomainVerification(BaseModel):
    completed: bool = False
    code: str
    code_prefixed: str = ""

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.code_prefixed = f"{SETTINGS.canary.domain_verify.prefix}{self.code}"


class CanaryModel(PublicCanaryModel):
    domain_verification: DomainVerification
    keypair: CanaryEd25519Model


class TrustedCanaryModel(BaseModel):
    public_key_hash: str
    signature: str = Field(
        ...,
        max_length=240,
        description="Domain & public key hash signature, base64 encoded",
    )


class NextCanaryEnum(Enum):
    tomorrow = "tomorrow"
    week = "week"
    fortnight = "fortnight"
    month = "month"
    quarter = "quarter"
    year = "year"


class CanaryConcernEnum(Enum):
    none = "none"
    mild = "mild"
    moderate = "moderate"
    severe = "severe"


class CreateCanaryWarrantModel(BaseModel):
    next_: NextCanaryEnum = Field(..., alias="next")


class CreatedCanaryWarrantModel(CustomJsonEncoder):
    id: ObjectId = Field(..., alias="_id")
    next_canary: datetime
    issued: datetime

    @validator("next_canary")
    def validate_next_canary(cls, value: datetime) -> str:
        return value.strftime("%Y-%m-%dT%H:%M:%S")

    @validator("issued")
    def validate_issued(cls, value: datetime) -> str:
        return value.strftime("%Y-%m-%dT%H:%M:%S")


class PublishCanaryWarrantModel(CustomJsonEncoder):
    signature: str = Field(
        ...,
        max_length=240,
        description="Hash signature, base64 encoded",
    )
    btc_latest_block: str = Field(..., max_length=64)
    statement: str = Field("", max_length=5500)
    file_hashes: Dict[str, str] = {}
    concern: CanaryConcernEnum

    @validator("file_hashes")
    def validate_file_hashes(cls, value: dict) -> dict:
        if len(value) > SETTINGS.canary.documents.max_amount:
            raise ValueError(
                f"Canary documents cannot exceed {SETTINGS.canary.documents.max_amount}"
            )

        for hash_ in value.values():
            if len(hash_) > 64:
                raise ValueError("File hash cannot exceed 64 characters")

        return value


class PublishedCanaryWarrantModel(PublishCanaryWarrantModel, CreatedCanaryWarrantModel):
    canary_id: ObjectId
    user_id: ObjectId
    active: bool

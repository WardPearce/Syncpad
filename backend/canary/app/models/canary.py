from datetime import datetime
from typing import Optional

from bson import ObjectId
from models.customs import CustomJsonEncoder
from pydantic import BaseModel, Field


class CreateCanaryModel(CustomJsonEncoder):
    domain: str = Field(
        ...,
        regex=r"(?i)^((?!(?:www|www\d+)\.)[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)+(?:[a-zA-Z]{2,})$",
    )
    about: str = Field(..., max_length=500)
    algorithms: str = Field(
        "ED25519+BLAKE2b", max_length=120, description="Algorithms used for canary"
    )


class PublicCanaryModel(CreateCanaryModel):
    id: ObjectId = Field(..., alias="_id")
    logo: Optional[str] = None
    user_id: ObjectId
    created: datetime


class DomainVerification(BaseModel):
    completed: bool = False
    code: str


class CanaryModel(PublicCanaryModel):
    domain_verification: DomainVerification
    public_key: str = Field(
        ..., max_length=44, description="ed25519 public key, base64 encoded"
    )

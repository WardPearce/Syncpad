from datetime import datetime
from typing import Optional

from bson import ObjectId
from models.customs import CustomJsonEncoder
from pydantic import BaseModel, Field


class SessionLocationModel(BaseModel):
    region: Optional[str] = None
    country: Optional[str] = None
    ip: Optional[str] = None


class CreateSessionModel(CustomJsonEncoder):
    expires: datetime
    record_kept_till: datetime
    created: datetime

    location: SessionLocationModel
    device: Optional[str] = None

    user_id: ObjectId


class SessionModel(CreateSessionModel):
    id: ObjectId = Field(..., alias="_id")

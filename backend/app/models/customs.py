from bson import Int64, ObjectId
from pydantic import BaseModel, Field


class CustomJsonEncoder(BaseModel):
    class Config:
        json_encoders = {
            ObjectId: lambda v: str(v),
            Int64: lambda v: int(v),
        }
        arbitrary_types_allowed = True


class IvField(BaseModel):
    iv: str = Field(
        ..., max_length=128, description="IV for cipher text, base64 encoded."
    )

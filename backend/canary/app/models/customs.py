from bson.objectid import ObjectId
from pydantic import BaseModel, Field


class ObjectIdStr(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v: ObjectId) -> str:
        if not isinstance(v, ObjectId):
            raise ValueError("Not a valid ObjectId")
        return str(v)


class IvField(BaseModel):
    iv: str = Field(
        ..., max_length=128, description="IV for cipher text, base64 encoded."
    )

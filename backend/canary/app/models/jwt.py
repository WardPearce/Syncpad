from app.models.customs import CustomJsonEncoder
from app.models.user import UserModel
from bson import ObjectId


class UserJtiModel(CustomJsonEncoder):
    jti: ObjectId
    user: UserModel

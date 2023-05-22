import pyotp
from app.env import SETTINGS
from app.models.customs import IvField, ObjectIdStr
from argon2.profiles import RFC_9106_LOW_MEMORY
from pydantic import BaseModel, EmailStr, Field


class EmailModel(BaseModel):
    email: EmailStr


class Argon2Modal(BaseModel):
    salt: str = Field(
        ...,
        max_length=64,
        description="Salt used for deriving account key, base64 encoded",
    )
    time_cost: int = Field(
        RFC_9106_LOW_MEMORY.time_cost,
        ge=RFC_9106_LOW_MEMORY.time_cost - 1,
        le=12,
        description="Time cost",
    )
    memory_cost: int = Field(
        RFC_9106_LOW_MEMORY.memory_cost,
        ge=RFC_9106_LOW_MEMORY.memory_cost - 1,
        le=3355443200,
        description="Memory cost",
    )


class PublicUserModel(BaseModel):
    kdf: Argon2Modal
    otp_completed: bool = False


class AccountEd25199Modal(BaseModel):
    public_key: str = Field(
        ..., max_length=44, description="ed25519 public key, base64 encoded"
    )


class AccountKeychainModal(IvField):
    cipher_text: str = Field(
        ...,
        max_length=82,
        description="Locally encrypted 32 byte key for keychain, base64 encoded",
    )


class __CreateUserShared(EmailModel):
    auth: AccountEd25199Modal
    keychain: AccountKeychainModal
    kdf: Argon2Modal

    signature: str = Field(
        ...,
        max_length=128,
        description="Locally signed with ed25519 private key to validate account data hasn't been changed. Base64 encoded",
    )  # Used for the client to validate our response.

    # Assumed client side algorithms being used, help for future proofing
    # if we need to move away from outdated algorithms.
    algorithms: str = Field(
        "XCHACHA20_POLY1305+ED25519+ARGON2+BLAKE2b+IV24+SALT16+KEY32",
        max_length=120,
        description="Algorithms used by client.",
    )


class CreateUserModel(__CreateUserShared):
    pass


class OtpModel(BaseModel):
    secret: str
    completed: bool = False
    provisioning_uri: str = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.provisioning_uri = self.__provisioning_uri()

    def __provisioning_uri(self) -> str:
        return pyotp.totp.TOTP(self.secret).provisioning_uri(
            issuer_name=SETTINGS.site_name
        )


class UserModel(__CreateUserShared, EmailModel):
    id: ObjectIdStr = Field(..., alias="_id")
    otp: OtpModel
    email_verified: bool = False


class UserLoginSignatureModel(BaseModel):
    signature: str = Field(..., description="to_sign signed with ed25519 private key")
    id: str = Field(..., alias="_id")


class UserToSignModel(BaseModel):
    to_sign: str = Field(..., description="to be signed with ed25519 private key")
    id: ObjectIdStr = Field(..., alias="_id")

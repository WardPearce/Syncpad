from typing import Optional

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
        RFC_9106_LOW_MEMORY.memory_cost,
        ge=3,
        le=12,
        description="Time cost",
    )
    memory_cost: int = Field(
        RFC_9106_LOW_MEMORY.memory_cost,
        ge=67108864,
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
    ed25199: AccountEd25199Modal
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
        "XSALSA20_POLY1305_MAC+ED25519+X25519+ARGON2+BLAKE2b+IV16+SALT16",
        max_length=120,
        description="Algorithms used by client.",
    )


class CreateUserModel(__CreateUserShared):
    pass


class OtpModel(BaseModel):
    secret: str
    completed: bool = False
    provisioning_uri: str


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
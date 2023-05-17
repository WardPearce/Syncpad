from enum import Enum

from litestar.exceptions import (
    NotAuthorizedException,
    NotFoundException,
    ValidationException,
)

ERROR_CODE_KEY = "error_code"


class ErrorCodes(Enum):
    user_not_found = 2001
    invalid_auth = 2002
    invalid_captcha = 2003
    email_taken = 2004
    otp_completed = 2005


class UserNotFoundException(NotFoundException):
    def __init__(
        self,
    ) -> None:
        super().__init__(
            detail="User not found",
            extra={ERROR_CODE_KEY: ErrorCodes.user_not_found.value},
        )


class InvalidAccountAuth(NotAuthorizedException):
    def __init__(
        self,
    ) -> None:
        super().__init__(
            detail="Invalid account auth",
            extra={ERROR_CODE_KEY: ErrorCodes.invalid_auth.value},
        )


class InvalidCaptcha(NotAuthorizedException):
    def __init__(
        self,
    ) -> None:
        super().__init__(
            detail="Invalid captcha",
            extra={ERROR_CODE_KEY: ErrorCodes.invalid_captcha.value},
        )


class OtpAlreadyCompleted(ValidationException):
    def __init__(
        self,
    ) -> None:
        super().__init__(
            detail="OTP setup is completed already",
            extra={ERROR_CODE_KEY: ErrorCodes.otp_completed.value},
        )


class EmailTaken(ValidationException):
    def __init__(
        self,
    ) -> None:
        super().__init__(
            detail="Email has already been registered",
            extra={ERROR_CODE_KEY: ErrorCodes.email_taken.value},
        )

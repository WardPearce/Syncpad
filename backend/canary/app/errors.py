from enum import Enum

from litestar.exceptions import NotAuthorizedException, NotFoundException

ERROR_CODE_KEY = "error_code"


class ErrorCodes(Enum):
    user_not_found = 2001
    invalid_auth = 2002
    invalid_captcha = 2003


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

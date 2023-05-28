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
    domain_validation = 2006
    local_domain = 2007
    canary_taken = 2008
    upload_too_big = 2009
    canary_not_found = 2010
    unsupported_file_type = 2011
    already_trusted_canary = 2012


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


class DomainValidationError(ValidationException):
    def __init__(
        self,
    ) -> None:
        super().__init__(
            detail="Domain validation failed",
            extra={ERROR_CODE_KEY: ErrorCodes.domain_validation.value},
        )


class LocalDomainInvalid(ValidationException):
    def __init__(
        self,
    ) -> None:
        super().__init__(
            detail="Local domains can't be used",
            extra={ERROR_CODE_KEY: ErrorCodes.local_domain.value},
        )


class CanaryTaken(ValidationException):
    def __init__(
        self,
    ) -> None:
        super().__init__(
            detail="Domain has already been registered",
            extra={ERROR_CODE_KEY: ErrorCodes.canary_taken.value},
        )


class CanaryAlreadyTrusted(ValidationException):
    def __init__(
        self,
    ) -> None:
        super().__init__(
            detail="That canary has already been saved as a trusted canary.",
            extra={ERROR_CODE_KEY: ErrorCodes.already_trusted_canary.value},
        )


class FileTooBig(ValidationException):
    def __init__(
        self,
    ) -> None:
        super().__init__(
            detail="Uploaded file is larger then the max upload size",
            extra={ERROR_CODE_KEY: ErrorCodes.upload_too_big.value},
        )


class UnsupportedFileType(ValidationException):
    def __init__(
        self,
    ) -> None:
        super().__init__(
            detail="Uploaded file is not supported",
            extra={ERROR_CODE_KEY: ErrorCodes.unsupported_file_type.value},
        )


class CanaryNotFoundException(NotFoundException):
    def __init__(
        self,
    ) -> None:
        super().__init__(
            detail="Canary not found",
            extra={ERROR_CODE_KEY: ErrorCodes.canary_not_found.value},
        )

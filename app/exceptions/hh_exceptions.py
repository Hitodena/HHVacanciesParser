from app.types import ErrorCodes

RETRYABLE = {
    ErrorCodes.NetworkErrors.TIMEOUT,
    ErrorCodes.NetworkErrors.CONNECTION_ERROR,
}


class HHParserError(Exception):
    def __init__(
        self,
        message: str,
        *,
        code: ErrorCodes.HHParserErrors,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.retryable = code in RETRYABLE


class CaptchaError(HHParserError):
    def __init__(self, message: str) -> None:
        super().__init__(
            message,
            code=ErrorCodes.HHParserErrors.CAPTCHA_REQUIRED,
        )


class AuthCredentialsError(HHParserError):
    def __init__(self, message: str) -> None:
        super().__init__(
            message,
            code=ErrorCodes.HHParserErrors.INVALID_LOGIN,
        )


class NoVacanciesFoundError(HHParserError):
    def __init__(self, message: str) -> None:
        super().__init__(
            message,
            code=ErrorCodes.HHParserErrors.NO_VACANCIES_FOUND,
        )

from app.exceptions.hh_exceptions import (
    AuthCredentialsError,
    CaptchaError,
    HHParserError,
    NoVacanciesFoundError,
)

__all__ = [
    "HHParserError",
    "AuthCredentialsError",
    "CaptchaError",
    "NoVacanciesFoundError",
]

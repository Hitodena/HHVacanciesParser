from enum import StrEnum


class HHParserErrors(StrEnum):
    CAPTCHA_REQUIRED = "CAPTCHA_REQUIRED"
    INVALID_LOGIN = "INVALID_LOGIN"
    NO_VACANCIES_FOUND = "NO_VACANCIES_FOUND"


class NetworkErrors(StrEnum):
    TIMEOUT = "TIMEOUT"
    CONNECTION_ERROR = "CONNECTION_ERROR"


class ParsingErrors(StrEnum):
    ELEMENT_NOT_FOUND = "ELEMENT_NOT_FOUND"


class DatabaseErrors(StrEnum):
    NO_PROXIES_FOUND = "NO_PROXIES_FOUND"


class ErrorCodes:
    HHParserErrors = HHParserErrors
    NetworkErrors = NetworkErrors
    ParsingErrors = ParsingErrors
    DatabaseErrors = DatabaseErrors

from enum import StrEnum


class JobSearchStatus(StrEnum):
    STARTED = "started"
    CAPTCHA_REQUIRED = "captcha required"
    ERROR = "error"
    INVALID_CREDENTIALS = "invalid credentials"
    SUCCESS = "success"


class JobParserStage(StrEnum):
    AUTH = "auth"
    SEARCH = "search"
    PARSING = "parsing vacancies"
    APPLY = "apply"
    COMPLETE = "complete"
    WAITING = "waiting"

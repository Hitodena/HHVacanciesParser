from enum import StrEnum


class JobSearchStatus(StrEnum):
    SUCCESS = "success"
    CAPTCHA_REQUIRED = "captcha_required"
    ERROR = "error"

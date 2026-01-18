from pydantic import BaseModel, Field


class Logs(BaseModel):
    """Logging configuration"""

    file_log_level: str = Field(
        default="INFO", description="Log level for file logging"
    )


class Selectors(BaseModel):
    """Selectors for HH.ru website"""

    # Auth
    login_button: str = Field(
        default="[data-qa='submit-button']",
        description="Login or submit button selector",
    )
    region_code: str = Field(
        default="[data-qa='magritte-phone-input-calling-code']",
        description="Region code for phone number",
    )
    region_list: str = Field(
        default="[data-qa='magritte-select-option-list']",
        description="List of regions",
    )
    phone_input: str = Field(
        default="[data-qa='magritte-phone-input-national-number-input']",
        description="Field for entering phone number",
    )
    email_option: str = Field(
        default="Почта", description="Option to login via email"
    )
    email_input: str = Field(
        default="[data-qa='applicant-login-input-email']",
        description="Email input field",
    )
    password_button: str = Field(
        default="[data-qa='expand-login-by-password']",
        description="Button to expand the login form by password",
    )
    password_input: str = Field(
        default="[data-qa='applicant-login-input-password']",
        description="Password input field",
    )

    # Vacancy Search
    pagination_block: str = Field(
        default="[data-qa='pager-block']", description="Pagination block"
    )
    search_button: str = Field(
        default="[data-qa='searchVacancy-button']", description="Search button"
    )
    search_input: str = Field(
        default="[data-qa='search-input']", description="Search input field"
    )
    vacancy_result: str = Field(
        default="[data-qa='vacancy-serp__results']",
        description="Container for search results",
    )
    vacancy_links: str = Field(
        default="a[data-qa='serp-item__title']",
        description="Links to vacancies in the results",
    )

    # Vacancy Application
    vacancy_response: str = Field(
        default="[data-qa='vacancy-response-link-top']",
        description="Button to respond to a vacancy",
    )
    vacancy_response_popup: str = Field(
        default="[data-qa='vacancy-response-submit-popup']"
    )
    additional_info: str = Field(
        default="[data-qa='additional-data-collector__popup-title']",
        description="Popup with additional information when responding to a vacancy",
    )
    additional_info_close: str = Field(
        "[data-qa='additional-data-collector__popup-close`]"
    )
    vacancy_applied: str = Field(
        "Вы откликнулись", description="Text indicating successful application"
    )
    additional_quest: str = Field(
        default="Для отклика необходимо ответить на несколько вопросов работодателя",
        description="Message indicating additional questions are required for application",
    )
    cover_letter_text: str = Field(
        default="Сопроводительное письмо обязательное для этой вакансии",
        description="Message indicating cover letter is required for this vacancy",
    )
    cover_letter_input: str = Field(
        default="[data-qa='vacancy-response-letter-input']",
        description="Input field for cover letter",
    )

    # Error Messages
    login_error: str = Field(
        default="Неправильные данные для входа. Пожалуйста, попробуйте снова.",
        description="Error message for incorrect login credentials",
    )
    captcha_alt_text: str = Field(
        default="captcha",
        description="Alt text for CAPTCHA image",
    )
    vacancy_not_found: str = Field(
        default="Попробуйте другие варианты поискового запроса или уберите фильтры",
        description="Message when no search results are found",
    )


class Retries(BaseModel):
    """Retry configuration"""

    max_connection_attempts: int = Field(
        default=3, description="Maximum number of connection retries"
    )
    max_proxy_get_attempts: int = Field(
        default=3, description="Maximum number of proxy retrieval retries"
    )


class Timeouts(BaseModel):
    """Timeout configuration"""

    connection_timeout: int = Field(
        default=30,
        description="Timeout for establishing a connection (in seconds)",
    )
    element_timeout: int = Field(
        default=15, description="Timeout for element loading (in seconds)"
    )


class Network(BaseModel):
    """Network configuration"""

    sleep_between_actions: int = Field(
        default=2, description="Sleep time between actions (in seconds)"
    )
    sleep_between_requests_min: float = Field(
        default=0.5,
        description="Minimum sleep time between requests (in seconds)",
    )
    sleep_between_requests_max: float = Field(
        default=2,
        description="Maximum sleep time between requests (in seconds)",
    )


class Parsing(BaseModel):
    """Parsing configuration"""

    hh_login_url: str = Field(
        default="https://hh.ru/account/login",
        description="URL for the login page",
    )

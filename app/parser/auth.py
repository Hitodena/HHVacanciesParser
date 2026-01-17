import asyncio

from checks import check_captcha, check_login
from core.config import Network, Parsing, Selectors, Timeouts
from loguru import logger
from playwright.async_api import Page

from app.exceptions.hh_exceptions import AuthCredentialsError, CaptchaError
from app.models import AuthCredentials, EmailAuth, PhoneAuth
from app.utils.click_utils import safe_click


async def login_with_email(page: Page, credentials: EmailAuth) -> None:
    """Log in to the website using email credentials.
    Args:
        page (Page): The Playwright page to log in on.
        credentials (EmailAuth): The email authentication credentials.
    Raises:
        AuthCredentialsError: If the login fails due to incorrect credentials.
        CaptchaError: If a captcha is detected on the page.
    """
    logger.bind(auth_type="email", login_email=credentials.email).info(
        "Starting email login"
    )
    await page.goto(Parsing.hh_login_url)

    login_button = page.locator(Selectors.login_button)
    await safe_click(
        login_button,
        Selectors.login_button,
        timeout=Timeouts.element_timeout,
        no_wait_after=False,
    )

    email_option = page.get_by_text(Selectors.email_option, exact=True)
    await safe_click(
        email_option,
        Selectors.email_option,
        timeout=Timeouts.element_timeout,
        no_wait_after=False,
    )

    email_input = page.locator(Selectors.email_input)
    await email_input.fill(credentials.email)

    await asyncio.sleep(Network.sleep_between_actions)

    password_button = page.locator(Selectors.password_button)
    await safe_click(
        password_button,
        Selectors.password_button,
        timeout=Timeouts.element_timeout,
        no_wait_after=False,
    )

    password_input = page.locator(Selectors.password_input)
    await password_input.fill(credentials.password.get_secret_value())

    await asyncio.sleep(Network.sleep_between_actions)

    submit_button = page.locator(Selectors.login_button)
    await safe_click(
        submit_button,
        Selectors.login_button,
        timeout=Timeouts.element_timeout,
        no_wait_after=False,
    )

    if await check_captcha(page):
        raise CaptchaError("Captcha detected during email login.")

    if not await check_login(page):
        raise AuthCredentialsError("Invalid email or password.")

    logger.bind(auth_type="email", login_email=credentials.email).success(
        "Email login successful"
    )


async def login_with_phone(page: Page, credentials: PhoneAuth) -> None:
    """Log in to the website using phone credentials.
    Args:
        page (Page): The Playwright page to log in on.
        credentials (PhoneAuth): The phone authentication credentials.
    Raises:
        AuthCredentialsError: If the login fails due to incorrect credentials.
        CaptchaError: If a captcha is detected on the page.
    """
    logger.bind(
        auth_type="phone",
        login_phone=credentials.phone,
        country=credentials.country.value,
    ).info("Starting phone login")
    await page.goto(Parsing.hh_login_url)

    login_button = page.locator(Selectors.login_button)
    await safe_click(
        login_button,
        Selectors.login_button,
        timeout=Timeouts.element_timeout,
        no_wait_after=False,
    )

    region_code = page.locator(Selectors.region_code)
    await safe_click(
        region_code,
        Selectors.region_code,
        timeout=Timeouts.element_timeout,
        no_wait_after=False,
    )

    option_list = page.locator(Selectors.region_list)
    await option_list.get_by_label(
        credentials.country.value, exact=True
    ).click()

    phone_input = page.locator(Selectors.phone_input)
    await phone_input.fill(credentials.phone)

    await asyncio.sleep(Network.sleep_between_actions)

    password_button = page.locator(Selectors.password_button)
    await safe_click(
        password_button,
        Selectors.password_button,
        timeout=Timeouts.element_timeout,
        no_wait_after=False,
    )

    password_input = page.locator(Selectors.password_input)
    await password_input.fill(credentials.password.get_secret_value())

    await asyncio.sleep(Network.sleep_between_actions)

    submit_button = page.locator(Selectors.login_button)
    await safe_click(
        submit_button,
        Selectors.login_button,
        timeout=Timeouts.element_timeout,
        no_wait_after=False,
    )

    if await check_captcha(page):
        raise CaptchaError("Captcha detected during phone login.")

    if not await check_login(page):
        raise AuthCredentialsError("Invalid phone number or password.")

    logger.bind(
        auth_type="phone",
        login_phone=credentials.phone,
        country=credentials.country.value,
    ).success("Phone login successful")


async def login(page: Page, credentials: AuthCredentials) -> None:
    """Log in to the website using the provided credentials.
    Args:
        page (Page): The Playwright page to log in on.
        credentials (AuthCredentials): The authentication credentials.
    Raises:
        AuthCredentialsError: If the login fails due to incorrect credentials.
        CaptchaError: If a captcha is detected on the page.
    """
    if isinstance(credentials, EmailAuth):
        await login_with_email(page, credentials)
    elif isinstance(credentials, PhoneAuth):
        await login_with_phone(page, credentials)
    else:
        raise AuthCredentialsError("Unsupported authentication method.")

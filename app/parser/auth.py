import asyncio

from loguru import logger
from playwright.async_api import Page

from ..core import Config
from ..exceptions import AuthCredentialsError, CaptchaError
from ..models import AuthCredentials, EmailAuth, PhoneAuth
from ..utils.click_utils import safe_click
from .checks import check_captcha, check_login


async def login_with_email(
    page: Page, credentials: EmailAuth, config: Config
) -> None:
    """Log in to the website using email credentials.
    Args:
        page (Page): The Playwright page to log in on.
        credentials (EmailAuth): The email authentication credentials.
        config (Config): The application configuration.
    Raises:
        AuthCredentialsError: If the login fails due to incorrect credentials.
        CaptchaError: If a captcha is detected on the page.
    """
    logger.bind(auth_type="email", login_email=credentials.email).info(
        "Starting email login"
    )
    await page.goto(
        config.parsing.hh_login_url,
        wait_until="domcontentloaded",
        timeout=config.timeouts.connection_timeout * 1000,
    )

    login_button = page.locator(config.selectors.login_button)
    await safe_click(
        login_button,
        config.selectors.login_button,
        timeout=config.timeouts.element_timeout * 1000,
        no_wait_after=False,
    )

    email_option = page.get_by_text(
        config.selectors.email_option, exact=True
    ).first
    await safe_click(
        email_option,
        config.selectors.email_option,
        timeout=config.timeouts.element_timeout * 1000,
        no_wait_after=False,
    )

    email_input = page.locator(config.selectors.email_input)
    await email_input.fill(credentials.email)

    await asyncio.sleep(config.network.sleep_between_actions)

    password_button = page.locator(config.selectors.password_button)
    await safe_click(
        password_button,
        config.selectors.password_button,
        timeout=config.timeouts.element_timeout * 1000,
        no_wait_after=False,
    )

    password_input = page.locator(config.selectors.password_input)
    await password_input.fill(credentials.password)

    await asyncio.sleep(config.network.sleep_between_actions)

    submit_button = page.locator(config.selectors.login_button)
    await safe_click(
        submit_button,
        config.selectors.login_button,
        timeout=config.timeouts.element_timeout * 1000,
        no_wait_after=False,
    )

    await page.wait_for_load_state(
        "domcontentloaded", timeout=config.timeouts.connection_timeout * 1000
    )
    await asyncio.sleep(config.network.sleep_between_actions)

    if await check_captcha(page, config):
        logger.error("Captcha detected during email login.")
        raise CaptchaError("Captcha detected during email login.")

    if not await check_login(page, config):
        logger.error("Login failed: invalid email or password.")
        raise AuthCredentialsError("Invalid email or password.")

    logger.bind(auth_type="email", login_email=credentials.email).success(
        "Email login successful"
    )


async def login_with_phone(
    page: Page, credentials: PhoneAuth, config: Config
) -> None:
    """Log in to the website using phone credentials.
    Args:
        page (Page): The Playwright page to log in on.
        credentials (PhoneAuth): The phone authentication credentials.
        config (Config): The application configuration.
    Raises:
        AuthCredentialsError: If the login fails due to incorrect credentials.
        CaptchaError: If a captcha is detected on the page.
    """
    logger.bind(
        auth_type="phone",
        login_phone=credentials.phone,
        country=credentials.country.value,
    ).info("Starting phone login")
    await page.goto(config.parsing.hh_login_url)

    login_button = page.locator(config.selectors.login_button)
    await safe_click(
        login_button,
        config.selectors.login_button,
        timeout=config.timeouts.element_timeout * 1000,
        no_wait_after=False,
    )

    region_code = page.locator(config.selectors.region_code)
    await safe_click(
        region_code,
        config.selectors.region_code,
        timeout=config.timeouts.element_timeout * 1000,
        no_wait_after=False,
    )

    option_list = page.locator(config.selectors.region_list)
    await option_list.get_by_text(credentials.country.value, exact=True).click(
        no_wait_after=False, timeout=config.timeouts.element_timeout * 1000
    )

    phone_input = page.locator(config.selectors.phone_input)
    await phone_input.fill(
        credentials.phone, timeout=config.timeouts.element_timeout * 1000
    )

    await asyncio.sleep(config.network.sleep_between_actions)

    password_button = page.locator(config.selectors.password_button)
    await safe_click(
        password_button,
        config.selectors.password_button,
        timeout=config.timeouts.element_timeout * 1000,
        no_wait_after=False,
    )

    password_input = page.locator(config.selectors.password_input)
    await password_input.fill(credentials.password)

    await asyncio.sleep(config.network.sleep_between_actions)

    submit_button = page.locator(config.selectors.login_button)
    await safe_click(
        submit_button,
        config.selectors.login_button,
        timeout=config.timeouts.element_timeout * 1000,
        no_wait_after=False,
    )

    await page.wait_for_load_state(
        "domcontentloaded", timeout=config.timeouts.connection_timeout * 1000
    )
    await asyncio.sleep(config.network.sleep_between_actions)

    if await check_captcha(page, config):
        logger.error("Captcha detected during phone login.")
        raise CaptchaError("Captcha detected during phone login.")

    if not await check_login(page, config):
        logger.error("Login failed: invalid phone number or password.")
        raise AuthCredentialsError("Invalid phone number or password.")

    logger.bind(
        auth_type="phone",
        login_phone=credentials.phone,
        country=credentials.country.value,
    ).success("Phone login successful")


async def login(
    page: Page, credentials: AuthCredentials, config: Config
) -> None:
    """Log in to the website using the provided credentials.
    Args:
        page (Page): The Playwright page to log in on.
        credentials (AuthCredentials): The authentication credentials.
        config (Config): The application configuration.
    Raises:
        AuthCredentialsError: If the login fails due to incorrect credentials.
        CaptchaError: If a captcha is detected on the page.
    """
    logger.debug(
        f"Login attempt with credentials type: {type(credentials)}, value: {credentials}"
    )
    if isinstance(credentials, EmailAuth):
        await login_with_email(page, credentials, config)
    elif isinstance(credentials, PhoneAuth):
        await login_with_phone(page, credentials, config)
    else:
        raise AuthCredentialsError(
            f"Unsupported authentication method with type: {type(credentials)}, value: {credentials}."
        )

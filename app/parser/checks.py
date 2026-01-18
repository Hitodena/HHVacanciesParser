from loguru import logger
from playwright.async_api import Page

from ..core import Config


async def check_login(page: Page, config: Config) -> bool:
    """Check if login was successful.
    Args:
        page (Page): The Playwright page after attempting login.
        config (Config): The application configuration.
    Returns:
        bool: True if login was successful, False otherwise.
    """
    logger.debug("Checking login status")
    try:
        login_error = page.get_by_text(
            config.selectors.login_error, exact=True
        )
        is_visible = await login_error.is_visible()
        return not is_visible
    except Exception:
        return True


async def check_captcha(page: Page, config: Config) -> bool:
    """Check if a captcha is present on the page.
    Args:
        page (Page): The Playwright page to check for captcha.
        config (Config): The application configuration.
    Returns:
        bool: True if captcha is present, False otherwise.
    """
    logger.debug("Checking for captcha")
    try:
        captcha1 = page.get_by_text(
            config.selectors.captcha_message_one, exact=True
        )
        captcha2 = page.get_by_text(
            config.selectors.captcha_message_two, exact=True
        )

        is_visible1 = await captcha1.is_visible()
        is_visible2 = await captcha2.is_visible()

        return is_visible1 or is_visible2
    except Exception:
        return False


async def check_no_vacancies(page: Page, config: Config) -> bool:
    """Check if no vacancies were found on the page.
    Args:
        page (Page): The Playwright page to check for vacancies.
        config (Config): The application configuration.
    Returns:
        bool: True if no vacancies were found, False otherwise.
    """
    logger.debug("Checking for no vacancies")
    try:
        no_results = page.get_by_text(
            config.selectors.vacancy_not_found, exact=True
        )
        return await no_results.is_visible()
    except Exception:
        return False

from loguru import logger
from playwright.async_api import Page

from app.core import Selectors


async def check_login(page: Page) -> bool:
    """Check if login was successful.
    Args:
        page (Page): The Playwright page after attempting login.
    Returns:
        bool: True if login was successful, False otherwise.
    """
    logger.debug("Checking login status")
    try:
        login_error = page.get_by_text(Selectors.login_error, exact=True)
        is_visible = await login_error.is_visible()
        return not is_visible
    except Exception:
        return True


async def check_captcha(page: Page) -> bool:
    """Check if a captcha is present on the page.
    Args:
        page (Page): The Playwright page to check for captcha.
    Returns:
        bool: True if captcha is present, False otherwise.
    """
    logger.debug("Checking for captcha")
    try:
        captcha1 = page.get_by_text(Selectors.captcha_message_one, exact=True)
        captcha2 = page.get_by_text(Selectors.captcha_message_two, exact=True)

        is_visible1 = await captcha1.is_visible()
        is_visible2 = await captcha2.is_visible()

        return is_visible1 or is_visible2
    except Exception:
        return False


async def check_no_vacancies(page: Page) -> bool:
    """Check if no vacancies were found on the page.
    Args:
        page (Page): The Playwright page to check for vacancies.
    Returns:
        bool: True if no vacancies were found, False otherwise.
    """
    logger.debug("Checking for no vacancies")
    try:
        no_results = page.get_by_text(Selectors.vacancy_not_found, exact=True)
        return await no_results.is_visible()
    except Exception:
        return False

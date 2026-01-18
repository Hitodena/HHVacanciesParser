from loguru import logger
from playwright.async_api import Page

from ..core import Config
from ..models import AuthCredentials


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
        login_error = page.get_by_text(config.selectors.login_error)
        is_visible = await login_error.is_visible(timeout=1000)
        return not is_visible
    except Exception as exc:
        logger.exception(f"Failed to check login errors: {exc}")
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
        dialog = page.get_by_role("dialog")
        captcha_img = dialog.get_by_alt_text(config.selectors.captcha_alt_text)
        return await captcha_img.is_visible(timeout=1000)
    except Exception as exc:
        logger.exception(f"Failed to check captcha : {exc}")
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
        return await no_results.is_visible(timeout=1000)
    except Exception as exc:
        logger.exception(
            f"Failed to check for vacancies after pagination: {exc}"
        )
        return False


async def check_additional_questions(page: Page, config: Config) -> bool:
    """Check if additional questions are required for application.
    Args:
        page (Page): The Playwright page to check for additional questions.
        config (Config): The application configuration.
    Returns:
        bool: True if additional questions are required, False otherwise.
    """
    logger.debug("Checking for additional questions")
    try:
        quest = page.get_by_text(config.selectors.additional_quest, exact=True)
        return await quest.is_visible(timeout=1000)
    except Exception:
        return False


async def check_required_letter(
    page: Page, config: Config, credentials: AuthCredentials
) -> bool:
    """Check if a cover letter is required and fill it if provided in credentials.
    Args:
        page (Page): The Playwright page to check for required cover letter.
        config (Config): The application configuration.
        credentials (AuthCredentials): The authentication credentials containing the cover letter.

    Returns:
        bool: True if cover questions passed down or there is no questions, False otherwise.
    """
    logger.bind(vacancy_url=page.url).debug(
        "Checking for required cover letter"
    )
    try:
        required = page.get_by_text(
            config.selectors.cover_letter_text, exact=True
        )
        if await required.is_visible(timeout=1000):
            logger.bind(vacancy_url=page.url).info(
                "Additional letter required for a vacancy"
            )
            if credentials.answer_req:
                dialog = page.get_by_role("dialog")
                letter_input = dialog.locator(
                    config.selectors.cover_letter_input
                )
                await letter_input.fill(credentials.answer_req)
                logger.bind(vacancy_url=page.url).debug("Filled cover letter")
                await dialog.locator(
                    config.selectors.vacancy_response_popup
                ).click(
                    timeout=config.timeouts.element_timeout,
                    no_wait_after=False,
                )
                logger.bind(vacancy_url=page.url).info(
                    "Letter applied for a vacancy"
                )
                return True
            else:
                logger.bind(vacancy_url=page.url).warning(
                    "Cover letter required but not provided in credentials"
                )
                return False
        return True
    except Exception:
        return False

import asyncio
import random

from loguru import logger
from playwright.async_api import Page, expect

from ..core import Config
from ..exceptions import CaptchaError
from ..models import AuthCredentials
from ..utils.click_utils import safe_click
from .checks import (
    check_additional_questions,
    check_captcha,
    check_required_letter,
)


async def apply_to_vacancy(
    page: Page, vacancy_url: str, config: Config, credentials: AuthCredentials
) -> bool:
    """Apply to a vacancy on the given page.
    Args:
        page (Page): The Playwright page to apply on.
        vacancy_url (str): The URL of the vacancy to apply to.
        config (Config): The application configuration.
        credentials (AuthCredentials): The authentication credentials.
    Returns:
        bool: True if the application was successful, False otherwise.
    Raises:
        CaptchaError: If a captcha is detected on the page.
    """
    logger.bind(vacancy_url=vacancy_url).info(
        "Starting application to vacancy"
    )
    await page.goto(
        vacancy_url,
        wait_until="domcontentloaded",
        timeout=config.timeouts.connection_timeout * 1000,
    )

    apply_button = page.locator(config.selectors.vacancy_response).first
    await safe_click(
        apply_button,
        config.selectors.vacancy_response,
        timeout=config.timeouts.element_timeout * 1000,
        no_wait_after=False,
    )

    await asyncio.sleep(config.network.sleep_between_actions)

    if await check_captcha(page, config):
        logger.error("Captcha detected during vacancy application.")
        raise CaptchaError("Captcha detected during vacancy application.")

    if await check_additional_questions(page, config):
        return False

    if not await check_required_letter(page, config, credentials):
        return False

    await close_application_modal(page, config)

    success_message = page.get_by_text(
        config.selectors.vacancy_applied, exact=True
    )
    try:
        await expect(success_message).to_be_visible(
            timeout=config.timeouts.element_timeout * 1000
        )
        next_application_delay = random.uniform(
            config.network.sleep_between_requests_min,
            config.network.sleep_between_requests_max,
        )
        logger.bind(
            vacancy_url=vacancy_url,
            next_application_s=round(next_application_delay, 2),
        ).success("Application successful")
        return True
    except Exception:
        return False


async def close_application_modal(page: Page, config: Config) -> None:
    """Close the application modal on the given page if appears.
    Args:
        page (Page): The Playwright page to close the modal on.
        config (Config): The application configuration.
    """
    try:
        logger.debug("Looking for application modal window")
        modal_window = page.locator(config.selectors.additional_info)
        await expect(modal_window).to_be_visible()

        close_button = page.locator(config.selectors.additional_info_close)
        await safe_click(
            close_button,
            config.selectors.additional_info_close,
            timeout=config.timeouts.element_timeout * 1000,
            no_wait_after=False,
        )
    except Exception:
        pass

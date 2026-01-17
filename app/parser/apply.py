import asyncio

from checks import check_captcha
from loguru import logger
from playwright.async_api import Page, expect

from app.core import Network, Selectors, Timeouts
from app.exceptions import CaptchaError
from app.utils.click_utils import safe_click


async def apply_to_vacancy(page: Page, vacancy_url: str) -> bool:
    """Apply to a vacancy on the given page.
    Args:
        page (Page): The Playwright page to apply on.
        vacancy_url (str): The URL of the vacancy to apply to.
    Returns:
        bool: True if the application was successful, False otherwise.
    Raises:
        CaptchaError: If a captcha is detected on the page.
    """
    logger.bind(vacancy_url=vacancy_url).info(
        "Starting application to vacancy"
    )
    await page.goto(vacancy_url, timeout=Timeouts.connection_timeout * 1000)

    apply_button = page.locator(Selectors.vacancy_response).first
    await safe_click(
        apply_button,
        Selectors.vacancy_response,
        timeout=Timeouts.element_timeout,
        no_wait_after=False,
    )

    await asyncio.sleep(Network.sleep_between_actions)

    if await check_captcha(page):
        raise CaptchaError("Captcha detected during vacancy application.")

    await close_application_modal(page)

    success_message = page.get_by_text(Selectors.vacancy_applied, exact=True)
    try:
        await expect(success_message).to_be_visible(
            timeout=Timeouts.element_timeout
        )
        logger.bind(vacancy_url=vacancy_url).success("Application successful")
        return True
    except Exception:
        return False


async def close_application_modal(page: Page) -> None:
    """Close the application modal on the given page if appears.
    Args:
        page (Page): The Playwright page to close the modal on.
    """
    try:
        modal_window = page.locator(Selectors.additional_info)
        await expect(modal_window).to_be_visible(
            timeout=Timeouts.element_timeout
        )

        close_button = page.locator(Selectors.additional_info_close)
        await safe_click(
            close_button,
            Selectors.additional_info_close,
            timeout=Timeouts.element_timeout,
            no_wait_after=False,
        )
    except Exception:
        pass

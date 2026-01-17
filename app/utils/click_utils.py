from loguru import logger
from playwright.async_api import Locator


async def safe_click(locator: Locator, selector: str, **kwargs) -> None:
    """Safely click a locator with logging and error handling.

    Args:
        locator (Locator): The Playwright locator to click.
        selector (str): The selector string for logging.
        **kwargs: Additional arguments to pass to click method.
    """
    logger.bind(selector=selector).debug("Clicking element")
    try:
        await locator.click(**kwargs)
    except Exception as exc:
        logger.bind(selector=selector).exception(
            f"Failed to click element: {exc}"
        )
        raise

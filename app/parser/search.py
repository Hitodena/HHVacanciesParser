import asyncio

from loguru import logger
from playwright.async_api import Page

from ..exceptions import CaptchaError, NoVacanciesFoundError
from ..utils.click_utils import safe_click
from .checks import check_captcha, check_no_vacancies


async def search_vacancies(page: Page, query: str, config) -> None:
    """Perform a vacancy search on the given page.
    Args:
        page (Page): The Playwright page to perform the search on.
        query (str): The search query string.
        config (Config): The application configuration.
    Raises:
        CaptchaError: If a captcha is detected on the page.
        NoVacanciesFoundError: If no vacancies are found for the given query.
    """
    logger.bind(query=query).info("Starting vacancy search")
    search_button = page.locator(config.selectors.search_button)
    await safe_click(
        search_button,
        config.selectors.search_button,
        timeout=config.timeouts.element_timeout * 1000,
    )

    await asyncio.sleep(config.network.sleep_between_actions)

    if await check_captcha(page, config):
        logger.error("Captcha detected during vacancy search.")
        raise CaptchaError("Captcha detected during vacancy search.")

    search_input = page.locator(config.selectors.search_input)
    await search_input.fill(
        query, timeout=config.timeouts.element_timeout * 1000
    )

    await asyncio.sleep(config.network.sleep_between_actions)

    await search_input.press("Enter", no_wait_after=False)

    await asyncio.sleep(config.network.sleep_between_actions)

    logger.bind(query=query).success("Vacancy search completed")


async def parse_vacancy_urls(page: Page, config) -> list[str]:
    """Parse vacancy URLs from the search results page.
    Args:
        page (Page): The Playwright page containing the search results.
        config (Config): The application configuration.
    Returns:
        list[str]: A list of vacancy URLs.
    """
    logger.bind(search_url=page.url).info("Parsing vacancy URLs")
    links: list[str] = []

    await page.wait_for_selector(
        config.selectors.vacancy_result,
        timeout=config.timeouts.element_timeout * 1000,
    )

    if await check_no_vacancies(page, config):
        logger.warning("No vacancies found for the query.")
        raise NoVacanciesFoundError("No vacancies found for the query.")

    vacancy_links = await page.query_selector_all(
        config.selectors.vacancy_links
    )

    for link in vacancy_links:
        url = await link.get_attribute("href")
        if url:
            links.append(url)

    logger.bind(search_url=page.url, vacancy_count=len(links)).success(
        "Vacancy URLs parsed"
    )
    return links


async def goto_page(page: Page, page_number: int, config) -> bool:
    """Navigate to a specific page number in the search results.
    Args:
        page (Page): The Playwright page to navigate.
        page_number (int): The page number to navigate to.
        config (Config): The application configuration.
    Returns:
        bool: True if navigation was successful, False otherwise.
    Raises:
        CaptchaError: If a captcha is detected on the page.
    """
    logger.bind(page_number=page_number).debug("Navigating to page")
    try:
        pagination_block = page.locator(config.selectors.pagination_block)
        page_button = pagination_block.get_by_text(str(page_number))
        await safe_click(
            page_button,
            f"{config.selectors.pagination_block} text:{page_number}",
            timeout=config.timeouts.element_timeout * 1000,
            no_wait_after=False,
        )

        if await check_captcha(page, config):
            logger.error("Captcha detected during pagination.")
            raise CaptchaError("Captcha detected during pagination.")

        if await check_no_vacancies(page, config):
            return False

        return True
    except Exception:
        return False

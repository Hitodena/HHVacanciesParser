import asyncio

from checks import check_captcha, check_no_vacancies
from loguru import logger
from playwright.async_api import Page

from app.core import Network, Selectors, Timeouts
from app.exceptions import CaptchaError, NoVacanciesFoundError
from app.utils.click_utils import safe_click


async def search_vacancies(page: Page, query: str) -> None:
    """Perform a vacancy search on the given page.
    Args:
        page (Page): The Playwright page to perform the search on.
        query (str): The search query string.
    Raises:
        CaptchaError: If a captcha is detected on the page.
        NoVacanciesFoundError: If no vacancies are found for the given query.
    """
    logger.bind(query=query).info("Starting vacancy search")
    search_button = page.locator(Selectors.search_button)
    await safe_click(
        search_button,
        Selectors.search_button,
        timeout=Timeouts.element_timeout,
    )

    await asyncio.sleep(Network.sleep_between_actions)

    if await check_captcha(page):
        raise CaptchaError("Captcha detected during vacancy search.")

    search_input = page.locator(Selectors.search_input)
    await search_input.fill(query, timeout=Timeouts.element_timeout)

    await asyncio.sleep(Network.sleep_between_actions)

    await search_input.press("Enter", no_wait_after=False)

    await asyncio.sleep(Network.sleep_between_actions)

    if await check_no_vacancies(page):
        raise NoVacanciesFoundError(f"No vacancies found for query: {query}")

    logger.bind(query=query).success("Vacancy search completed")


async def parse_vacancy_urls(page: Page) -> list[str]:
    """Parse vacancy URLs from the search results page.
    Args:
        page (Page): The Playwright page containing the search results.
    Returns:
        list[str]: A list of vacancy URLs.
    """
    logger.bind(search_url=page.url).info("Parsing vacancy URLs")
    links: list[str] = []

    await page.wait_for_selector(
        Selectors.vacancy_result, timeout=Timeouts.element_timeout
    )
    vacancy_links = await page.query_selector_all(Selectors.vacancy_links)

    for link in vacancy_links:
        url = await link.get_attribute("href")
        if url:
            links.append(url)

    logger.bind(search_url=page.url, vacancy_count=len(links)).success(
        "Vacancy URLs parsed"
    )
    return links


async def goto_page(page: Page, page_number: int) -> bool:
    """Navigate to a specific page number in the search results.
    Args:
        page (Page): The Playwright page to navigate.
        page_number (int): The page number to navigate to.
    Returns:
        bool: True if navigation was successful, False otherwise.
    Raises:
        CaptchaError: If a captcha is detected on the page.
    """
    logger.bind(page_number=page_number).debug("Navigating to page")
    try:
        pagination_block = page.locator(Selectors.pagination_block)
        page_button = pagination_block.get_by_text(str(page_number))
        await safe_click(
            page_button,
            f"{Selectors.pagination_block} text:{page_number}",
            timeout=Timeouts.element_timeout,
            no_wait_after=False,
        )

        if await check_captcha(page):
            raise CaptchaError("Captcha detected during pagination.")

        if await check_no_vacancies(page):
            return False

        return True
    except Exception:
        return False

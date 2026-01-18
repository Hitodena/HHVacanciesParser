import asyncio
import random

from loguru import logger
from playwright.async_api import Page

from ..core import Config
from ..custom_types import JobSearchStatus
from ..exceptions import CaptchaError, NoVacanciesFoundError
from ..models import AuthCredentials, JobSearchResult
from ..parser import (
    apply_to_vacancy,
    goto_page,
    login,
    parse_vacancy_urls,
    search_vacancies,
)


async def process_job_search(
    page: Page,
    config: Config,
    credentials: AuthCredentials,
    search_query: str,
    max_applications: int,
) -> JobSearchResult:
    """Process a job search workflow including login, search, parsing, and applications.

    This function performs the complete job search automation workflow. If website selectors
    change (e.g., due to UI updates), the function may fail with element not found errors.
    In such cases, update the selectors in config.toml and restart.

    Args:
        page (Page): The Playwright page to perform operations on.
        config (Config): The application configuration containing selectors, timeouts, etc.
        credentials (AuthCredentials): The authentication credentials for login.
        search_query (str): The search query string for job vacancies.
        max_applications (int, optional): Maximum number of applications to attempt. Defaults to 200.

    Returns:
        JobSearchResult: The result of the job search process, including status, applied count, total vacancies, and progress.

    Raises:
        CaptchaError: If a CAPTCHA is encountered during the process.
        Exception: If a element was not found
    """
    applied_count = 0
    total_vacancies = []
    result = JobSearchResult(
        status=JobSearchStatus.SUCCESS, applied=0, total=0, progress=0.0
    )

    try:
        # 1. Authorization
        await login(page, credentials, config)
        result.progress = 10

        # 2. Job search
        await search_vacancies(page, search_query, config)
        result.progress = 20

        # 3. Parsing vacancies with pagination
        current_page = 1
        while len(total_vacancies) < max_applications:
            try:
                vacancy_urls = await parse_vacancy_urls(page, config)
                total_vacancies.extend(vacancy_urls)
            except NoVacanciesFoundError as exc:
                logger.warning(f"No more vacancies found: {exc}")
                break

            if len(total_vacancies) >= max_applications:
                break

            current_page += 1
            if not await goto_page(page, current_page, config):
                break

        # Limit the number
        total_vacancies = total_vacancies[:max_applications]
        result.total = len(total_vacancies)
        result.progress = 30

        # 4. Applications
        for i, vacancy_url in enumerate(total_vacancies):
            progress = 30 + ((i + 1) / len(total_vacancies)) * 70

            try:
                success = await apply_to_vacancy(page, vacancy_url, config)
                if success:
                    applied_count += 1
                    result.applied = applied_count
            except CaptchaError:
                raise
            except Exception:
                pass

            result.progress = progress

            # Delay between applications
            delay = random.uniform(
                config.network.sleep_between_requests_min,
                config.network.sleep_between_requests_max,
            )
            await asyncio.sleep(delay)

        result.progress = 100.0
        return result

    except CaptchaError as exc:
        result.status = JobSearchStatus.CAPTCHA_REQUIRED
        result.message = str(exc)
        result.applied = applied_count
        return result
    except Exception as exc:
        result.status = JobSearchStatus.ERROR
        result.message = str(exc)
        result.applied = applied_count
        return result

import asyncio
import random
from typing import Callable

from loguru import logger
from playwright.async_api import Page

from ..core import Config
from ..custom_types import JobParserStage, JobSearchStatus
from ..exceptions import (
    AuthCredentialsError,
    CaptchaError,
    NoVacanciesFoundError,
)
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
    progress_callback: Callable | None = None,
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
        progress_callback (Callable): Function to update celery task progress

    Returns:
        JobSearchResult: The result of the job search process, including status, applied count, total vacancies, and progress.

    Raises:
        CaptchaError: If a CAPTCHA is encountered during the process.
        Exception: If a element was not found
    """
    applied_count = 0
    total_vacancies = []
    result = JobSearchResult(
        status=JobSearchStatus.STARTED, applied=0, total=0, progress=0.0
    )

    def update_progress(stage: JobParserStage, progress: float, **kwargs):
        """Update current progress and callback"""
        result.progress = progress
        if progress_callback:
            progress_callback(stage=stage, progress=progress, **kwargs)

    try:
        # 1. Authorization
        update_progress(JobParserStage.AUTH, 5)
        await login(page, credentials, config)
        update_progress(JobParserStage.AUTH, 10)

        # 2. Job search
        update_progress(JobParserStage.SEARCH, 15)
        await search_vacancies(page, search_query, config)
        update_progress(JobParserStage.SEARCH, 20)

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
        update_progress(JobParserStage.PARSING, 30, total=len(total_vacancies))

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

            update_progress(
                JobParserStage.APPLY,
                progress=progress,
                applied=applied_count,
                total=len(total_vacancies),
            )

            # Delay between applications
            delay = random.uniform(
                config.network.sleep_between_requests_min,
                config.network.sleep_between_requests_max,
            )
            await asyncio.sleep(delay)

        update_progress(JobParserStage.COMPLETE, 100, applied=applied_count)
        result.status = JobSearchStatus.SUCCESS
        return result

    except CaptchaError as exc:
        result.status = JobSearchStatus.CAPTCHA_REQUIRED
        result.message = str(exc)
        result.applied = applied_count
        return result
    except AuthCredentialsError as exc:
        result.status = JobSearchStatus.INVALID_CREDENTIALS
        result.message = str(exc)
        result.applied = applied_count
        return result
    except Exception as exc:
        result.status = JobSearchStatus.ERROR
        result.message = str(exc)
        result.applied = applied_count
        return result

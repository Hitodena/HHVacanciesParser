import asyncio
import random

from playwright.async_api import Page

from app.core import Network
from app.exceptions import CaptchaError
from app.models import AuthCredentials, JobSearchResult
from app.parser import (
    apply_to_vacancy,
    goto_page,
    login,
    parse_vacancy_urls,
    search_vacancies,
)
from app.types import JobSearchStatus


async def process_job_search(
    page: Page,
    credentials: AuthCredentials,
    search_query: str,
    max_applications: int = 200,
) -> JobSearchResult:
    applied_count = 0
    total_vacancies = []
    result = JobSearchResult(
        status=JobSearchStatus.SUCCESS, applied=0, total=0, progress=0.0
    )

    try:
        # 1. Authorization
        await login(page, credentials)
        result.progress = 10

        # 2. Job search
        await search_vacancies(page, search_query)
        result.progress = 20

        # 3. Parsing vacancies with pagination
        current_page = 1
        while len(total_vacancies) < max_applications:
            vacancy_urls = await parse_vacancy_urls(page)
            total_vacancies.extend(vacancy_urls)

            if len(total_vacancies) >= max_applications:
                break

            current_page += 1
            if not await goto_page(page, current_page):
                break

        # Limit the number
        total_vacancies = total_vacancies[:max_applications]
        result.total = len(total_vacancies)
        result.progress = 30

        # 4. Applications
        for i, vacancy_url in enumerate(total_vacancies):
            progress = 30 + ((i + 1) / len(total_vacancies)) * 70

            try:
                success = await apply_to_vacancy(page, vacancy_url)
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
                Network.sleep_between_requests_min,
                Network.sleep_between_requests_max,
            )
            await asyncio.sleep(delay)

        result.progress = 100.0
        return result

    except CaptchaError as exc:
        result.status = JobSearchStatus.CAPTCHA_REQUIRED
        result.message = str(exc)
        result.applied = applied_count
        return result
    except Exception as e:
        result.status = JobSearchStatus.ERROR
        result.message = str(e)
        result.applied = applied_count
        return result

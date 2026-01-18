import asyncio

from . import ENV_FILE
from .core import load
from .custom_types import HHCountryRegions
from .models import PhoneAuth
from .services import BrowserManager, process_job_search

config = load()
print(config)
print(ENV_FILE)

browser = BrowserManager(config)
creds = PhoneAuth(
    country=HHCountryRegions.BELARUS,
    phone="*****",
    password='(******)',  # type: ignore
)


async def main():
    await browser.start()

    async with browser.context() as page:
        await process_job_search(page, config, creds, "Бариста", 5)

    await browser.close()


asyncio.run(main())

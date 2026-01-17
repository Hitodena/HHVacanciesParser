from asyncio import run
from time import sleep

from fake_useragent import UserAgent
from playwright.async_api import Page, async_playwright, expect

ua = UserAgent(
    browsers=["Chrome", "Google"], os=["Windows"], platforms=["desktop"]
)


async def login():
    async with async_playwright() as plw:
        browser = await plw.chromium.launch(
            args=[
                "--disable-blink-features=AutomationControlled",
                "--enable-webgl",
                "--use-gl=swiftshader",
                "--enable-accelerated-2d-canvas",
            ],
            headless=False,
        )
        headers = {
            "User-Agent": ua.random,
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Connection": "keep-alive",
        }
        context = await browser.new_context(
            locale="ru-RU",
            timezone_id="Europe/Moscow",
            extra_http_headers=headers,
        )
        page = await context.new_page()
        await page.goto("https://hh.ru/account/login")
        login_button = page.locator("[data-qa='submit-button']")
        await login_button.click()

        region_code = page.locator(
            "[data-qa='magritte-phone-input-calling-code']"
        )
        await region_code.click()

        option_list = page.locator("[data-qa='magritte-select-option-list']")
        # Wait for the dropdown options to be visible
        await option_list.get_by_label("Беларусь").click()
        # sleep(5)

        input_field = page.locator(
            "[data-qa='magritte-phone-input-national-number-input']"
        )
        await input_field.fill("xxx")
        # sleep(5)

        # email_option = page.get_by_text("Почта", exact=True)
        # await email_option.click()

        # email_input = page.locator("[data-qa='applicant-login-input-email']")
        # await email_input.fill("xxx")

        with_password_button = page.locator(
            "[data-qa='expand-login-by-password']"
        )
        await with_password_button.click()

        password_input = page.locator(
            "[data-qa='applicant-login-input-password']"
        )
        await password_input.fill('xxx')
        sleep(5)

        submit_button = page.locator("[data-qa='submit-button']")
        await submit_button.click()
        is_captcha = await check_captcha(page)
        if is_captcha:
            print("Captcha detected, please solve it manually.")
            input("Press Enter after solving the captcha...")
        is_logged_in = await check_login(page)
        print(is_logged_in)

        await search(page)
        sleep(5)

        links = await parse_vacancies_to_urls(page)
        for link in links:
            print(link, end="\n")
        sleep(5)

        vacancy = links[0]
        is_applied = await apply_vacancy(page, vacancy)
        is_captcha = await check_captcha(page)
        if is_captcha:
            print("Captcha detected, please solve it manually.")
            input("Press Enter after solving the captcha...")
        print("Applied to vacancy:", is_applied)
        input()

        await browser.close()


async def pagination(page: Page, to_page: int):
    pagination_block = page.locator("[data-qa='pager-block']")
    await pagination_block.get_by_text(str(to_page)).click()
    if await check_no_vacancies(page):
        return False
    is_captcha = await check_captcha(page)
    if is_captcha:
        print("Captcha detected, please solve it manually.")
        input("Press Enter after solving the captcha...")


async def search(page: Page):
    search_button = page.locator("[data-qa='searchVacancy-button']")
    await search_button.click()

    is_captcha = await check_captcha(page)
    if is_captcha:
        print("Captcha detected, please solve it manually.")
        input("Press Enter after solving the captcha...")

    search_input = page.locator("[data-qa='search-input']")
    await search_input.fill("Разработчик")
    sleep(5)
    await search_input.press("Enter")


async def parse_vacancies_to_urls(page: Page):
    links: list[str] = []
    await page.wait_for_selector("[data-qa='vacancy-serp__results']")
    vacancy_links = await page.query_selector_all(
        "a[data-qa='serp-item__title']"
    )
    for link in vacancy_links:
        url = await link.get_attribute("href")
        if url:
            links.append(url)
    return links


async def apply_vacancy(page: Page, vacancy_url: str):
    await page.goto(vacancy_url)
    apply_button = page.locator("[data-qa='vacancy-response-link-top']").first
    await apply_button.click()
    is_captcha = await check_captcha(page)
    if is_captcha:
        print("Captcha detected, please solve it manually.")
        input("Press Enter after solving the captcha...")
    if page.get_by_text("Вы откликнулись", exact=True):
        return True


async def more_work_modal(page: Page):
    try:
        await expect(
            page.locator("[data-qa='additional-data-collector__popup-title']")
        ).to_be_visible(timeout=5000)
        await page.locator(
            "[data-qa='additional-data-collector__popup-close']"
        ).click()
    except Exception as e:
        print("No more work modal:", e)


async def check_login(page: Page):
    try:
        error_locator = page.get_by_text(
            "Неправильные данные для входа. Пожалуйста, попробуйте снова.",
            exact=True,
        )
        is_visible = await error_locator.is_visible()
        print(f"Login error message visible: {is_visible}")
        if is_visible:
            return False
        else:
            return True
    except Exception as e:
        print("No login errors found:", e)
        return True


async def check_captcha(page: Page):
    try:
        captcha1_locator = page.get_by_text("Пройдите капчу", exact=True)
        captcha2_locator = page.get_by_text(
            "Пожалуйста, подтвердите, что вы не робот", exact=True
        )
        is_visible1 = await captcha1_locator.is_visible()
        is_visible2 = await captcha2_locator.is_visible()
        print(f"Captcha text 1 visible: {is_visible1}")
        print(f"Captcha text 2 visible: {is_visible2}")
        if is_visible1 or is_visible2:
            return True
        else:
            return False
    except Exception as e:
        print("No captcha found:", e)
        return False


async def check_no_vacancies(page: Page):
    try:
        if page.get_by_text(
            "Попробуйте другие варианты поискового запроса или уберите фильтры",
            exact=True,
        ).is_visible():
            return True
    except Exception as e:
        print("Vacancies found:", e)
        return False


run(login())

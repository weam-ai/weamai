from src.logger.default_logger import logger
import asyncio
import os
from playwright.async_api import async_playwright, Page, Browser, Playwright, BrowserContext


async def scroll_to_bottom(page: Page, scroll_delay: float = 2.0):
    """
    Scrolls the page to the bottom to load dynamic content.
    """
    try:
        previous_height = await page.evaluate('document.body.scrollHeight')
        while True:
            await page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await asyncio.sleep(scroll_delay)
            current_height = await page.evaluate('document.body.scrollHeight')
            if current_height == previous_height:
                break
            previous_height = current_height
    except Exception as e:
        logger.error(f"Error during scrolling: {e}")
        raise


# async def launch_and_prepare_page(
#         url: str,
#         user_agent: str,
#         page_timeout: int,
#         scroll: bool,
#         scroll_delay: float
#     ) -> tuple[Playwright, Browser, Page]:
#         """
#         Launches the browser, creates the page context, navigates to the URL, and optionally scrolls.
#         Returns the playwright instance, browser, and page object for further use.
#         """
#         playwright = await async_playwright().start()
#         # browser = await playwright.chromium.launch(
#         #     headless=True,
#         #     args=[
#         #         "--disable-gpu",
#         #         "--no-sandbox",
#         #         "--single-process",
#         #         "--disable-dev-shm-usage",
#         #         "--no-zygote",
#         #         "--disable-setuid-sandbox",
#         #         "--disable-accelerated-2d-canvas",
#         #         "--disable-dev-shm-usage",
#         #         "--no-first-run",
#         #         "--no-default-browser-check",
#         #         "--disable-background-networking",
#         #         "--disable-background-timer-throttling",
#         #         "--disable-client-side-phishing-detection",
#         #         "--disable-component-update",
#         #         "--disable-default-apps",
#         #         "--disable-domain-reliability",
#         #         "--disable-features=AudioServiceOutOfProcess",
#         #         "--disable-hang-monitor",
#         #         "--disable-ipc-flooding-protection",
#         #         "--disable-popup-blocking",
#         #         "--disable-prompt-on-repost",
#         #         "--disable-renderer-backgrounding",
#         #         "--disable-sync",
#         #         "--force-color-profile=srgb",
#         #         "--metrics-recording-only",
#         #         "--mute-audio",
#         #         "--no-pings",
#         #         "--use-gl=swiftshader",
#         #         "--window-size=1280,1696"
#         #     ]
#         # )
#         CDP_ENDPOINT = os.getenv("PLAYWRIGHT_CDP_ENDPOINT")
#         browser = await playwright.chromium.connect(CDP_ENDPOINT)
#         logger.info("Connected to browser via CDP endpoint.")
#         # browser = await playwright.chromium.launch(
#         #     headless=True,
#         #     args=[
#         #         "--disable-gpu",
#         #         "--no-sandbox",
#         #         "--single-process",
#         #         "--disable-dev-shm-usage",
#         #         "--no-zygote",
#         #         "--disable-setuid-sandbox",
#         #         "--window-size=1280,1696",
#         #     ],
#         # )
#         context = await browser.new_context(user_agent=user_agent)
#         page = await context.new_page()
#         logger.info("Navigating to Fathom page...")
#         await page.goto(url, timeout=page_timeout, wait_until="networkidle")

#         if scroll:
#             logger.info("Scrolling enabled. Executing scroll to bottom...")
#             await scroll_to_bottom(page, scroll_delay)
#         else:
#             logger.info("Skipping scroll. Waiting briefly for page content.")
#             await page.wait_for_timeout(3000)

#         return playwright, browser, page

async def launch_and_prepare_page(
        url: str,
        user_agent: str,
        page_timeout: int,
        scroll: bool,
        scroll_delay: float
    ) -> tuple[Playwright, Browser, Page, BrowserContext]:
    """
    Launches the browser, creates the page context, navigates to the URL, and optionally scrolls.
    Returns the playwright instance, browser, page, and context for further use and cleanup.
    """
    playwright: Playwright = None
    browser: Browser = None
    context: BrowserContext = None
    page: Page = None

    try:
        playwright = await async_playwright().start()
        CDP_ENDPOINT = os.getenv("PLAYWRIGHT_CDP_ENDPOINT")
        browser = await playwright.chromium.connect(CDP_ENDPOINT)
        logger.info("Connected to browser via CDP endpoint.")
        context = await browser.new_context(user_agent=user_agent)
        page = await context.new_page()
        logger.info("Navigating to Fathom page...")
        await page.goto(url, timeout=page_timeout, wait_until="networkidle")

        if scroll:
            logger.info("Scrolling enabled. Executing scroll to bottom...")
            await scroll_to_bottom(page, scroll_delay)
        else:
            logger.info("Skipping scroll. Waiting briefly for page content.")
            await page.wait_for_timeout(3000)

        return playwright, browser, page, context

    except Exception as e:
        logger.error(f"Error preparing Playwright page: {e}")
        # Propagate the error so it can be caught in the caller
        raise
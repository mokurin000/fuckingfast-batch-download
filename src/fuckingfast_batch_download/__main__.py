import os
import asyncio
import logging
import urllib
import urllib.parse
from asyncio import Queue
from collections.abc import Coroutine

from playwright.async_api import async_playwright, Page, BrowserContext

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 GLS/100.10.9939.100"

TIMEOUT_PER_PAGE = int(os.environ.get("TIMEOUT_PER_PAGE", 5_000))
MAX_WORKERS = int(os.environ.get("MAX_WORKERS", 2))


async def worker_func(tasks: Queue[Coroutine]):
    while True:
        coro = await tasks.get()
        logger.info(
            f"Worker {asyncio.current_task().get_name()} executing task: {coro}"
        )
        await coro
        tasks.task_done()


async def extract_url_page(page: Page, url: str, close_page=False):
    logger.info(f"Navigating to URL: {url}")
    await page.goto(url)

    download_loc = page.locator("button.link-button")
    async with page.expect_download(timeout=TIMEOUT_PER_PAGE) as download_info:
        logger.info("Initiating download...")
        await download_loc.click()
        await download_loc.click()

    download = await download_info.value
    await download.cancel()
    if close_page:
        await page.close()

    filename = url.split("#")[-1]
    # Aria2c output
    print(download.url, f"    out={filename}", "    continue=true", sep="\n")
    logger.info(f"Download URL: {download.url}, Filename: {filename}")


async def extract_url_ctx(ctx: BrowserContext, url: str):
    page = await ctx.new_page()
    await extract_url_page(page, url, close_page=True)


async def main():
    with open("urls.txt", "r", encoding="utf-8") as urls:
        urls = [url for url in urls.read().split("\n") if url]

    async with async_playwright() as playwright:

        def on_page(page: Page):
            url = page.url
            parsed = urllib.parse.urlparse(url)

            if parsed.hostname is None:
                return
            if parsed.hostname != "fuckingfast.co":
                return page.close()

        logger.info("Launching browser...")
        browser = await playwright.chromium.launch(headless=False)
        ctx = await browser.new_context(user_agent=USER_AGENT, locale="en_US")
        ctx.on("page", on_page)
        await ctx.tracing.start(screenshots=True, snapshots=True, name="fuckingfast")

        if MAX_WORKERS > 1:
            tasks = Queue()
            workers = [
                asyncio.create_task(worker_func(tasks), name=f"worker_{i+1}")
                for i in range(MAX_WORKERS)
            ]

            for url in urls:
                await tasks.put(extract_url_ctx(ctx, url))
            await tasks.join()

            for worker in workers:
                worker.cancel()
        else:
            page = await ctx.new_page()
            for url in urls:
                await extract_url_page(page, url)

        await ctx.tracing.stop(path="trace.zip")
        await ctx.close()
        await browser.close()
        logger.info("Browser closed.")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"An error occurred: {e}")

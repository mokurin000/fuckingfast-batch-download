from aiofile import async_open
from playwright.async_api import Page, BrowserContext

from fuckingfast_batch_download.log import logger
from fuckingfast_batch_download.exceptions import RateLimited
from fuckingfast_batch_download.config import TIMEOUT_PER_PAGE


async def extract_url_page(page: Page, url: str, aria2c_file, close_page=False):
    logger.info(f"Navigating to URL: {url}")
    await page.goto(url)

    if "rate limit" in await page.content():
        raise RateLimited()
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
    async with async_open(aria2c_file, "a", encoding="utf-8") as f:
        await f.write(f"{download.url}\n    out={filename}\n    continue=true\n")
    logger.info(f"Download URL: {download.url}, Filename: {filename}")


async def extract_url_ctx(ctx: BrowserContext, url: str, aria2c_file):
    page = await ctx.new_page()
    await extract_url_page(page, url, aria2c_file, close_page=True)

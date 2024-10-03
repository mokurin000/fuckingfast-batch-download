from playwright.async_api import Page

from aiofiles.threadpool.text import AsyncTextIOWrapper
from fuckingfast_batch_download.log import logger
from fuckingfast_batch_download.exceptions import RateLimited, FileNotFound
from fuckingfast_batch_download.config import TIMEOUT_PER_PAGE


async def extract_url_page(
    page: Page, url: str, aria2c_file: AsyncTextIOWrapper, close_page=False
):
    filename = url.split("#")[-1]

    logger.info(f"Navigating to URL: {url}")
    await page.goto(url)

    if "rate limit" in await page.content():
        raise RateLimited()
    if await page.get_by_text("File Not Found Or Deleted").all():
        raise FileNotFound(filename=filename)

    download_loc = page.locator("button.link-button")
    async with page.expect_download(timeout=TIMEOUT_PER_PAGE) as download_info:
        logger.info(f"Initiating download for {filename}...")
        await download_loc.click()
        await download_loc.click()

    download = await download_info.value
    await download.cancel()
    if close_page:
        await page.close()

    await aria2c_file.write(f"{download.url}\n    out={filename}\n    continue=true\n")
    await aria2c_file.flush()
    logger.info(f"Download URL: {download.url}, Filename: {filename}")

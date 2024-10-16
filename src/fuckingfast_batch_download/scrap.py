from playwright.async_api import Page

from fuckingfast_batch_download import config
from fuckingfast_batch_download.log import logger
from fuckingfast_batch_download.exceptions import RateLimited, FileNotFound


async def extract_url_page(page: Page, url: str, close_page=False):
    """
    returns: tuple[uri, filename]
    """
    filename = url.split("#")[-1]

    logger.info(f"Navigating to URL: {url}")
    await page.goto(url, wait_until="domcontentloaded")

    if "rate limit" in await page.content():
        raise RateLimited()
    if await page.get_by_text("File Not Found Or Deleted").all():
        raise FileNotFound(filename=filename)

    download_loc = page.locator("button.link-button")
    async with page.expect_download(timeout=config.TIMEOUT_PER_PAGE) as download_info:
        logger.info(f"Initiating download for {filename}...")
        await download_loc.click()
        await download_loc.click()

    download = await download_info.value
    await download.cancel()
    if close_page:
        await page.close()

    logger.info(f"Download URL: {download.url}, Filename: {filename}")
    return (download.url, filename)

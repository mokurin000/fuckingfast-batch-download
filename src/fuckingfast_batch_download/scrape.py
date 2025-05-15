import re

from aiohttp import ClientSession

from fuckingfast_batch_download.log import logger
from fuckingfast_batch_download.exceptions import RateLimited, FileNotFound

DOWNLOAD_URL_REGEX = re.compile(
    r'window\.open\(\"(https://fuckingfast.co/dl/[^"]*)\"\)'
)


async def extract_url_page(session: ClientSession, url: str):
    """
    returns: tuple[uri, filename]
    """
    filename = url.split("#")[-1]

    async with session.get(url) as resp:
        content = await resp.text()

    if "rate limit" in content:
        raise RateLimited()
    if "File Not Found Or Deleted" in content:
        raise FileNotFound(filename=filename)

    download_url: str = DOWNLOAD_URL_REGEX.findall(content)[0]

    logger.info(f"Download URL: {download_url}, Filename: {filename}")
    return (download_url, filename)

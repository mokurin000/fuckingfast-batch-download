import asyncio
import argparse
import logging
from io import TextIOWrapper

import xdialog
from playwright.async_api import (
    async_playwright,
    BrowserContext,
    Error as PlaywrightError,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


async def scrape(
    ctx: BrowserContext,
    url: str,
    timeout: float,
    output_file: TextIOWrapper,
    skip_saved: bool,
):
    page = await ctx.new_page()
    logger.info(f"Navigating to {url}")
    await page.goto(url, wait_until="domcontentloaded", timeout=timeout)

    links_loc = page.get_by_text("Filehoster: FuckingFast")
    links = await links_loc.all()

    if len(links) != 1:
        message = "ERROR: please paste url of a game!"
        logger.error(message)
        xdialog.error(message=message)
        return

    hoster_links_elem = await page.locator("ul li div a").all()

    if hoster_links_elem:
        hoster_links = await asyncio.gather(
            *(tag.get_attribute("href") for tag in hoster_links_elem)
        )
    else:
        hoster_links = [await links[0].get_attribute("href")]

    fuckingfast_links = [
        link for link in hoster_links if link.startswith("https://fuckingfast.co")
    ]

    output_file.write("\n".join(fuckingfast_links) + "\n")
    output_file.flush()
    if not skip_saved:
        xdialog.info(message="saved url file!")


async def run(args):
    headless = not args.no_headless
    output_file: TextIOWrapper = args.output_file
    async with async_playwright() as playwright:
        try:
            browser = await playwright.chromium.launch(
                headless=headless, channel="msedge"
            )
        except PlaywrightError:
            browser = await playwright.chromium.launch(headless=headless)

        context = await browser.new_context()
        await context.tracing.start(name="fitgirl scrap", title="fitgirl scrap")
        try:
            await scrape(
                ctx=context,
                url=args.url,
                timeout=args.timeout,
                output_file=output_file,
                skip_saved=args.no_saved_dialog,
            )
        except PlaywrightError as e:
            xdialog.error(title="Scrap error", message=f"{e}")
        await context.tracing.stop(path="trace-fg.zip")
        await context.close()
        await browser.close()


def main(args):
    asyncio.run(run(args))


def _main():
    parser = argparse.ArgumentParser(
        description="Scrap fitgirl fuckingfast links and save to a file."
    )
    parser.add_argument("url", type=str, help="The URL to scrap")
    parser.add_argument(
        "--output-file",
        type=argparse.FileType("w", encoding="utf-8"),
        help="Save fetched links to this file",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=0,
        help="timeout (millisecond) for waiting page to load",
    )
    parser.add_argument(
        "--no-headless", help="disable headless mode", action="store_true"
    )
    parser.add_argument(
        "--no-saved-dialog", help="don't popup after saved", action="store_true"
    )
    args = parser.parse_args()

    main(args)


if __name__ == "__main__":
    _main()

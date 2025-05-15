import asyncio
import argparse
import logging
from io import TextIOWrapper

from bs4 import BeautifulSoup
import xdialog
from aiohttp import ClientSession

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


async def scrape(
    session: ClientSession,
    url: str,
    output_file: TextIOWrapper,
    skip_saved: bool,
):
    logger.info(f"fetching {url}")

    async with session.get(url) as resp:
        document = await resp.text()
    soup = BeautifulSoup(document, features="lxml")

    links = soup.find_all("a", string="Filehoster: FuckingFast")

    if len(links) != 1:
        message = "ERROR: please paste url of single game!"
        logger.error(message)
        xdialog.error(message=message)
        return

    hoster_links_elem = soup.select("ul li div a")

    if hoster_links_elem:
        hoster_links = [atag["href"] for atag in hoster_links_elem]
    else:
        hoster_links = [links[0]["href"]]

    fuckingfast_links = [
        link for link in hoster_links if link.startswith("https://fuckingfast.co")
    ]

    output_file.write("\n".join(fuckingfast_links) + "\n")
    output_file.flush()
    if not skip_saved:
        xdialog.info(message="saved url file!")


async def run(args):
    output_file: TextIOWrapper = args.output_file
    async with ClientSession() as session:
        await scrape(
            session=session,
            url=args.url,
            output_file=output_file,
            skip_saved=args.no_saved_dialog,
        )


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
        "--no-saved-dialog", help="don't popup after saved", action="store_true"
    )
    args = parser.parse_args()

    main(args)


if __name__ == "__main__":
    _main()

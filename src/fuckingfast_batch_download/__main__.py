import asyncio
import argparse
from asyncio import Queue
from argparse import Namespace
from collections.abc import Coroutine

from tqdm.asyncio import tqdm_asyncio
from tqdm.contrib.logging import logging_redirect_tqdm
from aiohttp import ClientSession

import fuckingfast_batch_download.config as config
from fuckingfast_batch_download.exceptions import FileNotFound, RateLimited
from fuckingfast_batch_download.log import logger
from fuckingfast_batch_download.scrape import extract_url_page
from fuckingfast_batch_download.utils import (
    consume_tasks,
    export_to_file,
)

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 GLS/100.10.9939.100"


async def worker_func(
    tasks: Queue[Coroutine],
    tqdm: tqdm_asyncio,
    session: ClientSession,
    results: list[tuple[str, str]],
):
    worker_name = asyncio.current_task().get_name()

    while True:
        payload = await tasks.get()
        if payload is None:
            tasks.task_done()
            break

        try:
            url = payload
            result = await extract_url_page(session, url)
            results.append(result)
        except RateLimited:
            logger.error("rate limit! exiting")

            tasks.task_done()
            await consume_tasks(tasks)
            break
        except FileNotFound as e:
            logger.warning(f"{e.filename} not found!")
        except TimeoutError as e:
            logger.warning(f"Timeout: {e.__cause__}")

        tqdm.update()
        tasks.task_done()
    logger.info(f"Worker {worker_name} exiting...")


def run_with_args(args: Namespace):
    config.MAX_WORKERS = int(args.max_workers)
    config.URLS_INPUT = args.urls_file
    config.ARIA2_OUTPUT = args.aria2c_file

    with logging_redirect_tqdm():
        asyncio.run(run())


async def concurrent_start(urls: list[str], session: ClientSession):
    tasks = Queue()
    tqdm = tqdm_asyncio(total=len(urls))
    results = []
    workers = [
        asyncio.create_task(
            worker_func(tasks, tqdm, session, results), name=f"worker_{i + 1}"
        )
        for i in range(config.MAX_WORKERS)
    ]

    for url in urls:
        await tasks.put(url)
    await tasks.join()

    if config.ARIA2_OUTPUT is not None:
        export_to_file(results, config.ARIA2_OUTPUT)

    for _ in workers:
        await tasks.put(None)
    for worker in workers:
        while not worker.done():
            await asyncio.sleep(0.5)


async def start(urls: list[str], session: ClientSession):
    results = []
    for url in tqdm_asyncio(urls):
        try:
            result = await extract_url_page(session, url)
            results.append(result)
        except RateLimited:
            logger.error("rate limit! exiting")
            break
        except FileNotFound as e:
            logger.warning(f"{e.filename} not found!")

    if config.ARIA2_OUTPUT is not None:
        export_to_file(results, config.ARIA2_OUTPUT)


async def run():
    urls = [url for url in config.URLS_INPUT.read().split("\n") if url]

    enable_concurrent = config.MAX_WORKERS > 1

    async with ClientSession() as session:
        if enable_concurrent:
            await concurrent_start(urls=urls, session=session)
        else:
            await start(urls=urls, session=session)


# The main function can be used as a CLI entrypoint
def main():
    parser = argparse.ArgumentParser(description="Web scraper with aria2c output")
    parser.add_argument(
        "urls_file",
        help="Input file containing URLs",
        type=argparse.FileType("r", encoding="utf-8"),
    )
    parser.add_argument(
        "aria2c_file",
        help="Output file for aria2c download links",
        type=argparse.FileType("w", encoding="utf-8"),
    )
    parser.add_argument(
        "--max-workers", type=int, default=2, help="Maximum number of workers"
    )
    args = parser.parse_args()
    run_with_args(args)


if __name__ == "__main__":
    main()

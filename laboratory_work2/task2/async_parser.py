import asyncio
import time

import aiohttp

from common.parser import process_page_async
from urls import urls


async def fetch(session, url):
    async with session.get(url, timeout=10, ssl=False) as response:
        text = await response.text()
        return url, text


async def parse_and_save(session, url):
    url, html = await fetch(session, url)
    if html:
        await process_page_async(html)


async def parse_chunk(session, chunk):
    tasks = [parse_and_save(session, url) for url in chunk]
    await asyncio.gather(*tasks)


async def main():
    num_chunks = 4
    start_time = time.time()

    chunk_size = (len(urls) + num_chunks - 1) // num_chunks
    chunks = [urls[i:i + chunk_size] for i in range(0, len(urls), chunk_size)]

    async with aiohttp.ClientSession() as session:
        chunk_tasks = [parse_chunk(session, chunk) for chunk in chunks]
        await asyncio.gather(*chunk_tasks)

    print(f"Количество задач: {len(urls)}")
    print(f"Время выполнения при помощи asyncio + aiohttp: {time.time() - start_time:.2f} секунд")


if __name__ == "__main__":
    asyncio.run(main())

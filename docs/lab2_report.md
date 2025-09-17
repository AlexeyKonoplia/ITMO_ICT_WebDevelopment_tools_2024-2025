# Лабораторная работа 2. Потоки. Процессы. Асинхронность.

## Цель
Понять отличия между потоками, процессами и асинхронностью в Python. Реализовать параллельные решения вычислительной задачи и парсинг веб‑страниц с сохранением результатов в БД.

## Задача 1. Сумма чисел (threading, multiprocessing, asyncio)

### threading
```python
import threading
import time


def calculate_sum(start, end, result, index):
    result[index] = sum(range(start, end))

target = 1000000000
num_threads = 4
chunk_size = target // num_threads
threads = []
results = [0] * num_threads
start_time = time.time()

for i in range(num_threads):
    start = i * chunk_size + 1
    end = (i + 1) * chunk_size + 1
    thread = threading.Thread(target=calculate_sum, args=(start, end, results, i))
    threads.append(thread)
    thread.start()

for thread in threads:
    thread.join()

total_sum = sum(results)

print(f"Количество потоков: {num_threads}")
print(f"Счёт до {target}")
print(f"Общая сумма: {total_sum}")
print(f"Время выполнения при помощи threading: {time.time() - start_time:.2f} секунд")
```

### multiprocessing
```python
import multiprocessing
import time

def calculate_sum(start_end):
    start, end = start_end
    return sum(range(start, end))

def main():
    target = 1000000000
    num_processes = 4
    chunk_size = target // num_processes
    ranges = [(i * chunk_size + 1, (i + 1) * chunk_size + 1) for i in range(num_processes)]
    start_time = time.time()

    with multiprocessing.Pool(processes=num_processes) as pool:
        results = pool.map(calculate_sum, ranges)

    total_sum = sum(results)
    print(f"Количество процессов: {num_processes}")
    print(f"Счёт до {target}")
    print(f"Общая сумма: {total_sum}")
    print(f"Время выполнения при помощи multiprocessing: {time.time() - start_time:.2f} секунд")

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')
    main()
```

### asyncio
```python
import asyncio
import time

async def calculate_sum(start, end):
    return sum(range(start, end))

async def main():
    target = 1000000000
    num_tasks = 4
    chunk_size = target // num_tasks
    tasks = []

    for i in range(num_tasks):
        start = i * chunk_size + 1
        end = (i + 1) * chunk_size + 1
        tasks.append(calculate_sum(start, end))

    start_time = time.time()
    results = await asyncio.gather(*tasks)
    total_sum = sum(results)
    print(f"Количество задач: {num_tasks}")
    print(f"Счёт до {target}")
    print(f"Общая сумма: {total_sum}")
    print(f"Время выполнения при помощи asyncio: {time.time() - start_time:.2f} секунд")

if __name__ == "__main__":
    asyncio.run(main())
```

## Задача 2. Параллельный парсинг и сохранение в БД

### Общие функции парсинга
```python
from bs4 import BeautifulSoup

from common.db import save_books, save_books_async


def extract_text(tag, default=""):
    return tag.text.strip() if tag else default


def extract_attr(tag, attr, default=None):
    return tag[attr] if tag and tag.has_attr(attr) else default


def parse_links_as_books(html):
    soup = BeautifulSoup(html, "html.parser")
    books = []

    for a_tag in soup.select("a[href]"):
        title = extract_text(a_tag)
        href = extract_attr(a_tag, "href")

        if not href or not title:
            continue

        if "/book/" in href:
            full_url = href if href.startswith("http") else f"https://www.litres.ru{href}"
            books.append({
                "title": title,
                "author": "—",
                "description": full_url,
                "year": None,
                "genre_name": None
            })

    return books


def process_page(html, url=""):
    print(f"[INFO] Обрабатывается: {url}")
    books_data = parse_links_as_books(html)
    if books_data:
        save_books(books_data)
    else:
        print("[INFO] Книжные ссылки не найдены.")


async def process_page_async(html, url=""):
    print(f"[INFO] Обрабатывается: {url}")
    books_data = parse_links_as_books(html)
    if books_data:
        await save_books_async(books_data)
```

### threading
```python
import threading
import time

import requests

from common.parser import process_page
from urls import urls


def parse_and_save(url_list):
    for url in url_list:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        process_page(response.text, url=url)


def main():
    num_threads = 4
    start_time = time.time()
    chunk_size = (len(urls) + num_threads - 1) // num_threads
    chunks = [urls[i:i + chunk_size] for i in range(0, len(urls), chunk_size)]

    threads = []
    for chunk in chunks:
        thread = threading.Thread(target=parse_and_save, args=(chunk,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print(f"Количество потоков: {num_threads}")
    print(f"Время выполнения при помощи threading: {time.time() - start_time:.2f} секунд")

if __name__ == "__main__":
    main()
```

### multiprocessing
```python
import multiprocessing
import time

import requests

from common.parser import process_page
from urls import urls


def parse_and_save(url_list):
    for url in url_list:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        process_page(response.text)


def main():
    start_time = time.time()
    num_processes = 4
    chunk_size = (len(urls) + num_processes - 1) // num_processes
    chunks = [urls[i:i + chunk_size] for i in range(0, len(urls), chunk_size)]
    processes = []

    for chunk in chunks:
        process = multiprocessing.Process(target=parse_and_save, args=(chunk,))
        processes.append(process)
        process.start()

    for process in processes:
        process.join()

    print(f"Количество процессов: {num_processes}")
    print(f"Время выполнения при помощи multiprocessing: {time.time() - start_time:.2f} секунд")

if __name__ == "__main__":
    main()
```

### asyncio + aiohttp
```python
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
```

## Выводы
- **threading**: подходит для IO‑bound задач (сетевые вызовы), ограничен GIL для CPU‑bound.
- **multiprocessing**: масштабируется для CPU‑bound задач, но дороже по памяти и IPC.
- **asyncio**: показывает лучшую производительность на большом числе сетевых запросов, требует асинхронных библиотек.

## Сравнительная таблица

| Критерий | threading | multiprocessing | asyncio |
|---|---|---|---|
| Парадигма | Потоки в одном процессе | Отдельные процессы | Кооперативная многозадачность |
| Задания | Лучше IO‑bound | Лучше CPU‑bound | Лучше множество IO‑bound |
| GIL | Общий на все потоки (мешает CPU) | Нет общего GIL между процессами | Есть GIL, но не критичен для IO |
| Масштабируемость по ядрам | Низкая для CPU | Высокая | Неприменимо (IO) |
| Память | Дешевая | Дороже (копии процессов) | Дешевая |
| Межзадачное взаимодействие | Общая память, синхронизация | IPC/очереди, сериализация | Общая петля событий, очереди |
| Простота отладки | Средняя | Сложнее (fork/spawn, IPC) | Средняя, нужна дисциплина async |
| Типичные библиотеки | requests, threading | multiprocessing, concurrent.futures | asyncio, aiohttp |
| Когда выбирать | Немного параллельных IO | Тяжелые CPU‑вычисления | Много сетевых запросов |

import aiohttp
from bs4 import BeautifulSoup


from common.db import save_books, save_books_async


async def fetch(session, url):
    async with session.get(url, timeout=10, ssl=False) as response:
        text = await response.text()
        return url, text


async def parse_and_save(url):
    async with aiohttp.ClientSession() as session:
        url, html = await fetch(session, url)
        if html:
            process_page_async(html)


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
                "author": "Unknown",
                "description": full_url,
                "year": None,
                "genre_name": "General"
            })

    return books


def process_page(html, url=""):
    print(f"[INFO] Обрабатывается: {url}")
    books_data = parse_links_as_books(html)
    if books_data:
        save_books(books_data)
    else:
        print("[INFO] Книжные ссылки не найдены.")


def process_page_async(html, url=""):
    print(f"[INFO] Обрабатывается: {url}")
    books_data = parse_links_as_books(html)
    print(f"[INFO] Найдено книг: {len(books_data)}")
    if books_data:
        try:
            save_books_async(books_data)
            print(f"[INFO] Сохранено книг: {len(books_data)}")
        except Exception as e:
            print(f"[ERROR] Ошибка при сохранении книг: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("[INFO] Книжные ссылки не найдены.")

from bs4 import BeautifulSoup
from config import DEAL_TYPE


def parse_list_page(html: str):
    if not html:
        print("❌ Не удалось загрузить страницу, пропускаем")
        return []

    soup = BeautifulSoup(html, "lxml")
    listings = []

    items = soup.select('[data-name="CardComponent"]')
    for item in items:
        url_tag = item.select_one(f'a[href*="cian.ru/{DEAL_TYPE}/flat/"]')
        url = url_tag["href"] if url_tag else None

        address_tags = item.select('a[data-name="GeoLabel"]')
        address_parts = []
        for tag in address_tags:
            text = tag.get_text(strip=True)
            if text:
                address_parts.append(text)
        address = ", ".join(address_parts) if address_parts else None

        if url:
            listings.append({
                "url": url,
                "address": address
            })

    return listings


def parse_total_listings(html):
    if not html:
        print("❌ Не удалось загрузить страницу, пропускаем")
        return 0

    soup = BeautifulSoup(html, "lxml")

    info = soup.select_one('h5[class*="color_text-primary-default"]')
        
    if info:
        text = info.get_text(strip=True)
    else:
        return 0

    count = ''
    for i in text:
        if i.isdigit(): count += i
    count = int(count)

    return count


def extract_next_page_url(html: str) -> str | None:
    soup = BeautifulSoup(html, "lxml")

    next_btn = soup.select_one(
        'div[class*="pagination-section"] a[class*="link-button"][href]'
    )

    if not next_btn:
        return None

    return next_btn.get("href")

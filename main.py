import random
import sys
import time

from config import BASE_URL, DELAY_BETWEEN_ADS, DELAY_BETWEEN_PAGES, LIMITS, ROOMS
from parsers.detail_parser import parse_detail_page
from parsers.fetcher import create_session, fetch_html
from parsers.list_parser import (
    extract_next_page_url,
    parse_list_page,
    parse_total_listings,
)
from utils.file_paths import OUTPUT_FILE
from utils.json_writer import JsonWriter
from utils.price_ranges import build_url, generate_price_ranges


def main():
    session = create_session()
    total_parsed_ads = 0

    price_ranges = generate_price_ranges(LIMITS)

    print(f"\n📁 Данные будут сохранены в файл: {OUTPUT_FILE}")

    with JsonWriter(OUTPUT_FILE) as writer:
        for rng in price_ranges:
            active_url = build_url(BASE_URL, rng)

            print(f"\n\nФильтры: ", end="")
            if rng["min"] is not None:
                print(f"мин. {rng['min']} ", end="")
            if rng["max"] is not None:
                print(f"макс. {rng['max']}", end="")
            print("")

            first_html = fetch_html(session, active_url)
            total_listings = parse_total_listings(first_html)

            if total_listings == 0:
                print(active_url)
                print("\t(Нет объявлений для заданных фильтров)")
                continue

            print(f"Всего объявлений по заданным фильтрам: {total_listings}")
            print(active_url)

            parsed_ads_for_range = 0

            current_url = active_url
            page_num = 1

            while current_url:
                print(f"\n🔍 Загружаем страницу {page_num}...")
                sys.stdout.flush()

                list_html = fetch_html(session, current_url)
                if list_html is None:
                    print("\t❌ Не удалось загрузить страницу, пропускаем.")
                    break

                listings = parse_list_page(list_html)
                if not listings:
                    print("⚡ Больше объявлений нет, завершаем разбор диапазона.")
                    break

                # Check if we have reached the total listings needed for this range
                remaining_needed = total_listings - parsed_ads_for_range
                if remaining_needed <= 0:
                    break

                if len(listings) > remaining_needed:
                    listings = listings[:remaining_needed]

                print(f"Найдено {len(listings)} объявлений")

                time.sleep(random.uniform(*DELAY_BETWEEN_PAGES))

                for listing in listings:
                    url = listing["url"]
                    print(
                        f"📄 [{total_parsed_ads + 1}] Парсим страницу объявления: {url}"
                    )
                    sys.stdout.flush()

                    detail_html = fetch_html(session, url)
                    if detail_html is None:
                        print(f"\t❌ Не удалось загрузить объявление: {url}")
                        continue

                    detail_data = parse_detail_page(detail_html)

                    result = {
                        "title": detail_data.get("title", ""),
                        "price": detail_data.get("price"),
                        "rooms": ROOMS,
                        "address": listing.get("address"),
                        "coordinates": detail_data.get("coordinates"),
                        "url": url,
                        "metro": detail_data.get("metro"),
                        "description": detail_data.get("description"),
                        "attributes": detail_data.get("attributes"),
                    }

                    writer.write(result)

                    parsed_ads_for_range += 1
                    total_parsed_ads += 1

                    time.sleep(random.uniform(*DELAY_BETWEEN_ADS))

                next_url = extract_next_page_url(list_html)

                if not next_url:
                    print("📌 Кнопка 'Дальше' отсутствует — последняя страница.")
                    break

                current_url = next_url
                page_num += 1

    print(
        f"\n✅ Всего обработано {total_parsed_ads} объявлений. "
        f"Данные сохранены в {OUTPUT_FILE}\n"
    )


if __name__ == "__main__":
    main()

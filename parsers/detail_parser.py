from bs4 import BeautifulSoup
import re


def parse_detail_page(html: str) -> dict:
    soup = BeautifulSoup(html, "lxml")
    data = {}

    title_tag = soup.select_one('h1[class*="title"]')
    data["title"] = title_tag.get_text(strip=True) if title_tag else None

    price_container = soup.select_one('[data-testid="price-amount"]')
    data["price"] = (
        int("".join(price_container.get_text().split()[:-1]))
        if price_container
        else None
    )

    data["metro"] = []
    stations = soup.select('a[class*="underground_link"]')
    times = soup.select('span[class*="underground_time"]')
    time_i = 0  # для случаев, когда вместо времени написано еще что-то
    for i in range(len(stations)):
        station_name = stations[i].get_text(strip=True)
        while "мин." not in times[i + time_i].get_text(strip=True):
            time_i += 1
        time_to_station = (
            int(times[i + time_i].get_text().split()[0])
            if (times[i + time_i].get_text().split()[0]).isdigit()
            else times[i + time_i].get_text(strip=True)
        )
        data["metro"].append({"station": station_name, "time": time_to_station})

    desc_tag = soup.select_one('[data-name="Description"]')
    data["description"] = desc_tag.get_text(strip=True) if desc_tag else None

    data["attributes"] = {"apartment": {}, "building": {}}
    groups = soup.select('div[data-name="OfferSummaryInfoGroup"]')

    for idx, group in enumerate(groups):
        target = "apartment" if idx == 0 else "building"

        items = group.select('div[data-name="OfferSummaryInfoItem"]')
        for item in items:
            paragraphs = item.find_all("p")
            if len(paragraphs) >= 2:
                key = paragraphs[0].get_text(strip=True)
                value = paragraphs[1].get_text(strip=True)
                if key and value:
                    data["attributes"][target][key] = value

        if target == "apartment" and "Общая площадь" in data["attributes"][target]:
            if isfloat(
                data["attributes"][target]["Общая площадь"][:-2]
                .strip()
                .replace(",", ".")
            ):
                data["attributes"][target]["Общая площадь"] = float(
                    data["attributes"][target]["Общая площадь"][:-2].replace(",", ".")
                )

    data["coordinates"] = extract_coordinates(str(soup))

    return data


def extract_coordinates(soup) -> tuple[float, float] | None:
    html = str(soup)
    match = re.search(
        r'"coordinates"\s*:\s*\{\s*"lat"\s*:\s*([-+]?\d*\.\d+|\d+)\s*,\s*"lng"\s*:\s*([-+]?\d*\.\d+|\d+)',
        html,
    )
    if match:
        lat = float(match.group(1))
        lng = float(match.group(2))
        return lat, lng
    return None


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False

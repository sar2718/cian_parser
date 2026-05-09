import json
import clickhouse_connect
import os
from dotenv import load_dotenv

load_dotenv()

client = clickhouse_connect.get_client(
    host=os.environ.get("CLICKHOUSE_HOST", "localhost"),
    port=int(os.environ.get("CLICKHOUSE_PORT", 8123)),
    username=os.environ.get("CLICKHOUSE_USER", "default"),
    password=os.environ.get("CLICKHOUSE_PASSWORD", "")
)

try:
    print(client.command("SELECT 1"))
    print("Подключение к ClickHouse успешно!")
except Exception as e:
    print("Ошибка подключения:", e)


def load_json(path):
    try:
        client.command("TRUNCATE TABLE cian_ads")
    except Exception as e:
        print("Ошибка TRUNCATE:", e)
        return
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    batch = []
    for ad in data: 
        coords = ad.get("coordinates", [0, 0])
        lat = float(coords[0]) if len(coords) > 0 else 0.0
        lon = float(coords[1]) if len(coords) > 1 else 0.0

        attributes = ad.get("attributes", {})
        apt = dict(attributes).get("apartment", {})
        build = dict(attributes).get("building", {})
        building_year = int(dict(build).get("Год постройки") or 0)
        total_area = dict(apt).get("Общая площадь")
        material_type = dict(build).get("Тип дома", "")
        house_types = dict(apt).get("Тип жилья", "")
        housing_type = [t.strip().capitalize() for t in house_types.split("/") if t.strip()]
        address = ad.get("address", "")

        district = None
        if address:
            parts = address.split(',')
            if len(parts) >= 2:
                dist = parts[1].strip()
                if dist and dist.isupper():
                    district = dist



        batch.append([
            ad.get("title", ""),
            float(ad.get("price", 0)),
            int(ad.get("rooms", 0)),
            ad.get("address", ""),
            district,
            lat,
            lon,
            float(total_area),
            housing_type,
            building_year,
            material_type,
            ad.get("url", ""),
            json.dumps(ad.get("attributes", {}), ensure_ascii=False),
            json.dumps(ad.get("metro", []), ensure_ascii=False)
        ])

    client.insert(
        "cian_ads",
        batch,
        column_names=[
            "title",
            "price",
            "rooms",
            "address",
            "district",
            "lat",
            "lon",
            "total_area",
            "housing_type",
            "building_year",
            "material_type",
            "url",
            "attributes",
            "metro"
        ]
    )

    print(f"Загружено {len(batch)} объявлений")

load_json("unique.json")

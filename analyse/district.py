import os
import clickhouse_connect
import numpy as np
from collections import defaultdict
from dotenv import load_dotenv
import json

load_dotenv()

client = clickhouse_connect.get_client(
    host=os.environ.get("CLICKHOUSE_HOST", "localhost"),
    port=int(os.environ.get("CLICKHOUSE_PORT", 8123)),
    username=os.environ.get("CLICKHOUSE_USER", "default"),
    password=os.environ.get("CLICKHOUSE_PASSWORD", ""),
)

client.command("SELECT 1")
print("Подключение к ClickHouse успешно!")

query = """
SELECT address, price, total_area
FROM cian_ads
WHERE price > 0 AND total_area > 0
"""

rows = client.query(query).result_rows
print(f"Получено {len(rows)} объявлений")

district_groups = defaultdict(list)

for address, price, area in rows:
    if not address:
        continue
    parts = address.split(",")
    district = parts[1].strip()
    if not district[0].isupper():
        continue
    if len(parts) < 2:
        continue
    district = parts[1].strip()
    price_m2_thousands = (price / 1000) / area
    district_groups[district].append(price_m2_thousands)

district_stats = {}
for district, prices in district_groups.items():
    median = np.median(prices)
    mean = np.mean(prices)
    count = len(prices)
    district_stats[district] = {
        "median_price_m2": median,
        "mean_price_m2": mean,
        "count_ads": count,
    }

output_dir = "analysis"
os.makedirs(output_dir, exist_ok=True)

with open(os.path.join(output_dir, "district_stats.json"), "w", encoding="utf-8") as f:
    json.dump(district_stats, f, ensure_ascii=False, indent=2)

print("Статистика по округам сохранена в district_stats.json")

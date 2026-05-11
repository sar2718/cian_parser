import os

import clickhouse_connect
import matplotlib.pyplot as plt
import numpy as np
from dotenv import load_dotenv

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
SELECT price, total_area
FROM cian_ads
WHERE price > 0
  AND total_area > 0
"""

rows = client.query(query).result_rows

prices_rub = np.array([r[0] for r in rows], dtype=float)
areas = np.array([r[1] for r in rows], dtype=float)

print(f"Получено {len(prices_rub)} объявлений")

prices_mln = prices_rub / 1_000_000
price_m2_th = (prices_rub / areas) / 1_000


def limits(data, low=1, high=99):
    return np.percentile(data, low), np.percentile(data, high)


output_dir = "analysis"
os.makedirs(output_dir, exist_ok=True)

xmin, xmax = limits(price_m2_th)

plt.figure(figsize=(10, 6))
plt.hist(price_m2_th, bins=80, range=(xmin, xmax), edgecolor="black")
plt.xlabel("Цена за м² (тыс. руб.)")
plt.ylabel("Количество объявлений")
plt.title("Распределение цены за квадратный метр")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "hist_price_m2.png"), dpi=200)
plt.close()

xmin, xmax = limits(prices_mln)

plt.figure(figsize=(10, 6))
plt.hist(prices_mln, bins=80, range=(xmin, xmax), edgecolor="black")
plt.xlabel("Цена квартиры (млн руб.)")
plt.ylabel("Количество объявлений")
plt.title("Распределение полной цены квартир")
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "hist_total_price.png"), dpi=200)
plt.close()

print("Гистограммы построены.")

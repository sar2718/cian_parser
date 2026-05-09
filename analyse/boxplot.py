import os
import numpy as np
import matplotlib.pyplot as plt
import clickhouse_connect
from collections import defaultdict
from dotenv import load_dotenv

load_dotenv()

client = clickhouse_connect.get_client(
    host=os.environ.get("CLICKHOUSE_HOST", "localhost"),
    port=int(os.environ.get("CLICKHOUSE_PORT", 8123)),
    username=os.environ.get("CLICKHOUSE_USER", "default"),
    password=os.environ.get("CLICKHOUSE_PASSWORD", "")
)

client.command("SELECT 1")
print("Подключение к ClickHouse успешно!")

query = """
SELECT rooms, price, total_area
FROM cian_ads
WHERE price > 0
  AND total_area > 0
  AND rooms BETWEEN 1 AND 5
"""

rows = client.query(query).result_rows

print(f"Получено {len(rows)} объявлений")

groups = defaultdict(list)

for rooms, price, area in rows:
    price_m2_thousands = (price / 1000) / area
    groups[rooms].append(price_m2_thousands)

labels = []
data = []

for rooms in sorted(groups.keys()):
    values = groups[rooms]
    if len(values) >= 100: 
        labels.append(f"{rooms}")
        data.append(values)

print("Группы:", {label: len(values) for label, values in zip(labels, data)})

# Построение boxplot
output_dir = "analysis"
os.makedirs(output_dir, exist_ok=True)

plt.figure(figsize=(10, 6))
plt.boxplot(
    data,
    tick_labels=labels,
    showfliers=False
)

all_values = np.concatenate(data)
ymin, ymax = np.percentile(all_values, [1, 99])
plt.ylim(ymin, ymax)

plt.ylabel("Цена за м² (тыс. руб.)")
plt.xlabel("Количество комнат")
plt.title("Распределение цены за м² по количеству комнат")
plt.grid(axis="y", alpha=0.4)
plt.tight_layout()
plt.savefig(os.path.join(output_dir, "boxplot_price_m2_by_rooms.png"), dpi=200)
plt.close()

print("Boxplot сохранён.")

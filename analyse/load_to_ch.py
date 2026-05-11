import os

import clickhouse_connect
from dotenv import load_dotenv

load_dotenv()

client = clickhouse_connect.get_client(
    host=os.environ.get("CLICKHOUSE_HOST", "localhost"),
    port=int(os.environ.get("CLICKHOUSE_PORT", 8123)),
    username=os.environ.get("CLICKHOUSE_USER", "default"),
    password=os.environ.get("CLICKHOUSE_PASSWORD", ""),
)

try:
    client.command("SELECT 1")
    print("Подключение к ClickHouse успешно!")
except Exception as e:
    print("Ошибка подключения:", e)
    exit(1)

client.command("""
CREATE TABLE IF NOT EXISTS cian_ads (
    id UUID DEFAULT generateUUIDv4(),
    title String,
    price Float64,
    rooms Int8,
    address Nullable(String),
    district Nullable(String),
    lat Float64,
    lon Float64,
    total_area Float64,
    housing_type Array(String),
    building_year Nullable(Int32),
    material_type Nullable(String),
    url String,
    attributes String,
    metro String,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY id
""")

print("Таблица создана!")

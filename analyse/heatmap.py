import folium
import branca.colormap as cm
import clickhouse_connect
import h3
from branca.colormap import LinearColormap
from collections import defaultdict
from shapely.geometry import Polygon, mapping
import numpy as np
import os
from dotenv import load_dotenv


def stream_ads(client, filters=None):

    price_min = filters.get("price_min")
    price_max = filters.get("price_max")
    rooms = filters.get("rooms")
    housing_type = filters.get("housing_type")
    total_area_min = filters.get("total_area_min")
    total_area_max = filters.get("total_area_max")
    building_year_min = filters.get("building_year_min")
    building_year_max = filters.get("building_year_max")
    material_type = filters.get("material_type")
    metro_time_max = filters.get("metro_time_max")
    district = filters.get("district")

    conditions = ["lat != 0", "lon != 0", "price > 0", "total_area > 0"]

    if price_min is not None:
        conditions.append(f"price >= {price_min}")
    if price_max is not None:
        conditions.append(f"price <= {price_max}")
    if rooms is not None:
        conditions.append(f"rooms = {rooms}")
    if housing_type is not None:
        types_list = "[" + ", ".join([f"'{t}'" for t in housing_type]) + "]"
        conditions.append(f"hasAll(housing_type, {types_list})")
    if total_area_min is not None:
        conditions.append(f"total_area >= {total_area_min}")
    if total_area_max is not None:
        conditions.append(f"total_area <= {total_area_max}")
    if building_year_min is not None:
        conditions.append(f"building_year >= {building_year_min}")
    if building_year_max is not None:
        conditions.append(f"building_year <= {building_year_max}")
    if material_type is not None:
        conditions.append(f"material_type = {material_type}")
    if district is not None:
        conditions.append(f"district = '{district}'")
    if isinstance(metro_time_max, int):
        conditions.append(
            "arrayMin(arrayMap(x -> JSONExtractInt(x, 'time'), JSONExtractArrayRaw(metro))) <= "
            f"{metro_time_max}"
        )

    where_clause = ""
    if conditions:
        where_clause = "WHERE " + " AND ".join(conditions)

    sql = f"""
        SELECT price, total_area, lat, lon
        FROM cian_ads
        {where_clause}
    """
    with client.query_rows_stream(sql) as stream:
        for row in stream:
            yield row


def handle_ad(ad_row, hex_stats, resolution=8):
    price, total_area, lat, lon = ad_row
    if not lat or not lon or not total_area or total_area <= 0:
        return
    price_m2 = price / total_area
    hex_id = h3.latlng_to_cell(lat, lon, resolution)
    hex_stats[hex_id]["sum_price_m2"] += price_m2
    hex_stats[hex_id]["count"] += 1

def process_ads_stream(client, resolution=8, filters=None):
    hex_stats = defaultdict(lambda: {"sum_price_m2": 0.0, "count": 0})
    for row in stream_ads(client, filters):
        handle_ad(row, hex_stats, resolution)
    return hex_stats

def hexagons_to_features(hex_stats):
    features = []
    for hex_id, stats in hex_stats.items():
        avg = stats["sum_price_m2"] / stats["count"]
        boundary = h3.cell_to_boundary(hex_id)
        boundary = [[lon, lat] for lat, lon in boundary]
        polygon = Polygon(boundary)
        features.append({
            "type": "Feature",
            "id": hex_id,
            "geometry": mapping(polygon),
            "properties": {
                "avg_price_m2": round(avg, 2),
                "count": stats["count"]
            }
        })
    return {"type": "FeatureCollection", "features": features}

def build_map(feature_collection, center=[55.75, 37.62], zoom=10, output="heatmap.html"):
    vals = []
    for f in dict(feature_collection).get("features", []):
        try:
            v = float(f["properties"]["avg_price_m2"])
            if v > 0:
                vals.append(v)
        except Exception:
            continue
    if not vals:
        print("Нет данных для colormap.")
        return
    
    vmin = np.percentile(vals, 30)
    vmed = np.percentile(vals, 70)
    vmax = np.percentile(vals, 95)
    v99 = np.percentile(vals, 99.5)

    colors = [
        "#1a9850",
        "#fee08b",
        "#d73027",
        "#000000"
    ]
    colormap = LinearColormap(
        colors=colors,
        index=[vmin, vmed, vmax, v99],
        vmin=vmin,
        vmax=v99
    )
    colormap.caption = "Средняя цена за м² (₽)"
    m = folium.Map(location=center, zoom_start=zoom, tiles="CartoDB positron")
    def style_fn(feature):
        try:
            v = float(feature["properties"]["avg_price_m2"])
            color = colormap(v) if v is not None else "#ffffff"
        except Exception:
            color = "#ffffff"
        return {
            "fillColor": color,
            "color": "gray",
            "weight": 0.3,
            "fillOpacity": 0.7,
        }
    
    folium.GeoJson(
        feature_collection,
        style_function=style_fn,
        tooltip=folium.GeoJsonTooltip(
            fields=["avg_price_m2", "count"],
            aliases=["Средняя цена за м² (₽):", "Объявлений:"],
            localize=True
            )
    ).add_to(m)
    colormap.add_to(m)
    m.save(output)
    print(f"Карта сохранена в {output}")



def main():
    filters = {
        "price_min": None,     
        "price_max": None,
        "rooms": None,
        "housing_type": None,
        "total_area_min": None,
        "total_area_max": None,
        "building_year_min": None,
        "building_year_max": None,
        "material_type": None,
        "metro_time_max": None,
        "district": "ЦАО"
    }

    load_dotenv()
    hex_resolution = 8

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
    
    hex_stats = process_ads_stream(
        client,
        resolution=hex_resolution,
        filters=filters
    )
    print(f"Гексагонов найдено: {len(hex_stats)}")
    print("Создание GeoJSON...")
    feature_collection = hexagons_to_features(hex_stats)
    print("Генерация карты...")
    build_map(feature_collection)

if __name__ == "__main__":
    main()

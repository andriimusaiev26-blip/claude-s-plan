
import json
import math
from pathlib import Path
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd

# Відкриті дані OpenStreetMap
SOURCE = "https://www.openstreetmap.org/copyright"
API_URL = "https://overpass-api.de/api/interpreter"

DATA_FILE = Path(__file__).parent / "data" / "aed_kyiv.csv"


def load_aeds():
    """Завантажує реальні AED у Києві з OpenStreetMap."""

    # Якщо дані вже завантажені, використовуємо CSV
    if DATA_FILE.exists():
        return pd.read_csv(DATA_FILE)

    query = """
    [out:json][timeout:30];
    nwr["emergency"="defibrillator"]
       (50.34,30.30,50.58,30.75);
    out center;
    """

    request = Request(
        API_URL,
        data=urlencode({"data": query}).encode("utf-8"),
        headers={
            "User-Agent": "KSE-OpenData-Hackathon/1.0"
        }
    )

    with urlopen(request, timeout=45) as response:
        data = json.load(response)

    locations = []

    for item in data.get("elements", []):
        tags = item.get("tags", {})
        coords = item.get("center", item)

        lat = coords.get("lat")
        lon = coords.get("lon")

        if lat is None or lon is None:
            continue

        locations.append({
            "name": tags.get("name", "Дефібрилятор AED"),
            "latitude": lat,
            "longitude": lon,
            "location": tags.get(
                "defibrillator:location", "Не вказано"
            ),
            "access": tags.get("access", "Невідомо"),
            "osm_id": str(item["id"]),
        })

    df = pd.DataFrame(locations)

    if df.empty:
        raise ValueError("Не знайдено даних про AED")

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(DATA_FILE, index=False)

    return df


def calculate_distance(lat1, lon1, lat2, lon2):
    """Відстань між двома точками у кілометрах."""
    radius = 6371

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)

    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(phi1)
        * math.cos(phi2)
        * math.sin(dlon / 2) ** 2
    )

    return 2 * radius * math.asin(math.sqrt(a))


def find_nearest_aeds(latitude, longitude, count=5):
    """Знаходить найближчі AED за координатами."""
    df = load_aeds().copy()

    df["distance_km"] = df.apply(
        lambda row: calculate_distance(
            latitude,
            longitude,
            row["latitude"],
            row["longitude"]
        ),
        axis=1
    )

    return df.sort_values("distance_km").head(count)


if __name__ == "__main__":
    # Тестова точка: центр Києва
    nearest = find_nearest_aeds(50.4501, 30.5234)

    print("Найближчі дефібрилятори:")
    print(nearest[["name", "distance_km", "location"]])
    print("Джерело: OpenStreetMap contributors (ODbL)")

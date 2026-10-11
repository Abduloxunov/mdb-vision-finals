"""Build kb/workshops.csv from OpenStreetMap (Overpass API) data for Tashkent.

Usage:
    python kb/tools/osm_workshops.py --fetch          # query Overpass, save stripped snapshots to kb/raw/
    python kb/tools/osm_workshops.py                  # rebuild kb/workshops.csv from the saved snapshots

Data: (c) OpenStreetMap contributors, ODbL 1.0 (https://www.openstreetmap.org/copyright).
Contact tags (phone, email, contact:*) are dropped on save: we do not redistribute personal contact data.
The workshop category is inferred from the name and service tags with the keyword rules below;
it is a heuristic and is marked as such in the `category_basis` column.
"""
import argparse
import csv
import json
import re
import urllib.parse
import urllib.request
from pathlib import Path

KB = Path(__file__).resolve().parents[1]
RAW = KB / "raw"
SNAPSHOT_DATE = "2026-10-11"
REPAIR_FILE = RAW / f"osm_tashkent_repair_{SNAPSHOT_DATE}.json"
DEALER_FILE = RAW / f"osm_tashkent_car_dealers_{SNAPSHOT_DATE}.json"
AREA = 'area["name:en"="Tashkent"]["admin_level"="4"]->.a;'
QUERIES = {
    REPAIR_FILE: '(nwr["shop"="car_repair"](area.a);nwr["shop"="tyres"](area.a);nwr["craft"="car_repair"](area.a);'
                 'nwr["shop"="car"]["service"](area.a);nwr["amenity"="car_wash"]["service:vehicle:car_repair"](area.a););',
    DEALER_FILE: '(nwr["shop"="car"](area.a););',
}
DROP_TAG = re.compile(r"^(phone|email|fax|contact:.*|mobile)$")

# Order matters: first match wins.
RULES = [
    ("not_repair", r"тонир|tonir|тюнинг|tuning|детейлинг|detailing|керамик|чехл|starline|pandora|security|bass|teyes|поезд|мед |офис|автозапчаст|запчаст|do'kon|магазин"),
    ("tyres", r"шиномонтаж|вулканиз|vulkaniz|shina|колес|koleso|подкачк|disk|диск|goodyear"),
    ("oil_change", r"замена масл|масл|castrol|mobil|liqui|mannol|enoc|oil"),
    ("electrical", r"электр|elektr|electr|аккум|akkum|galvan"),
    ("body", r"кузов|kuzov|сварн|body"),
    ("glass", r"стекл|glass|oyna"),
    ("ac", r"кондицион|konditsion"),
    ("suspension", r"развал|razval|ходов|амортиз|amortiz"),
    ("transmission", r"кпп|коробк|transmiss"),
    ("engine", r"мотор|двигат|токар"),
    ("gas_lpg_cng", r"гбо|метан|metan|gas"),
    ("inspection", r"техосмотр|texosmotr"),
]
SERVICE_TAGS = {
    "service:vehicle:tyres": "tyres", "service:vehicle:oil_change": "oil_change",
    "service:vehicle:electrical": "electrical", "service:vehicle:glass": "glass",
    "service:vehicle:diagnostics": "general", "service:vehicle:car_repair": "general",
}
BRANDS = {
    "chevrolet": r"chevrolet|шевроле|daewoo|дэу|gm uzbekistan|uzauto|автотехсервис|autotexservis",
    "byd": r"\bbyd\b|megawatt",
    "toyota": r"toyota|тойота",
    "hyundai": r"hyundai", "lada": r"lada|лада|ваз", "isuzu": r"isuzu", "man": r"\bman\b", "bmw": r"bmw",
}


def fetch():
    RAW.mkdir(exist_ok=True)
    for path, body in QUERIES.items():
        q = f"[out:json][timeout:90];{AREA}{body}out center tags;"
        req = urllib.request.Request(
            "https://overpass-api.de/api/interpreter",
            data=urllib.parse.urlencode({"data": q}).encode(),
            headers={"User-Agent": "mdb-vision-hackathon-kb/0.1"},
        )
        with urllib.request.urlopen(req, timeout=150) as r:
            data = json.load(r)
        save_stripped(data, path)


def save_stripped(data, path):
    for e in data["elements"]:
        e["tags"] = {k: v for k, v in e.get("tags", {}).items() if not DROP_TAG.match(k)}
    data.pop("generator", None)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=0), encoding="utf-8")


def coords(e):
    return (e["lat"], e["lon"]) if "lat" in e else (e["center"]["lat"], e["center"]["lon"])


def classify(tags, dealer):
    text = " ".join(str(tags.get(k, "")) for k in ("name", "name:ru", "name:en", "brand", "operator", "description")).lower()
    brands = [b for b, rx in BRANDS.items() if re.search(rx, text)]
    if dealer:
        return "brand_dealer", "osm shop=car (showroom; service not confirmed)", brands
    if tags.get("shop") == "tyres":
        return "tyres", "osm tag shop=tyres", brands
    for cat, rx in RULES:
        if re.search(rx, text):
            return cat, "name keyword (heuristic)", brands
    for tag, cat in SERVICE_TAGS.items():
        if tags.get(tag) == "yes":
            return cat, f"osm tag {tag}", brands
    if brands:
        return "brand_service", "osm brand tag or brand in name", brands
    return "general", "default for shop=car_repair", brands


def address(tags):
    parts = [tags.get("addr:street", ""), tags.get("addr:housenumber", "")]
    return " ".join(p for p in parts if p).strip()


def build():
    rows, seen = [], set()
    for path, dealer in ((REPAIR_FILE, False), (DEALER_FILE, True)):
        for e in json.loads(path.read_text(encoding="utf-8"))["elements"]:
            key = f"{e['type']}/{e['id']}"
            if key in seen:
                continue
            seen.add(key)
            t = e["tags"]
            cat, basis, brands = classify(t, dealer)
            if cat == "not_repair":
                continue
            if dealer and not brands and "service" not in t:
                continue  # generic used-car lots are not useful for repair matching
            lat, lon = coords(e)
            rows.append({
                "workshop_id": f"osm_{e['type'][0]}{e['id']}",
                "name": t.get("name", ""),
                "name_ru": t.get("name:ru", ""),
                "category": cat,
                "category_basis": basis,
                "brands": ";".join(brands),
                "lat": round(lat, 6),
                "lon": round(lon, 6),
                "address": address(t),
                "opening_hours": t.get("opening_hours", ""),
                "website": t.get("website", ""),
                "osm_url": f"https://www.openstreetmap.org/{e['type']}/{e['id']}",
                "source_ids": "S14" if dealer else "S13",
                "verified_by_team": "no",
            })
    rows.sort(key=lambda r: (r["category"], r["name"] == "", r["name"]))
    out = KB / "workshops.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"{len(rows)} workshops -> {out}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fetch", action="store_true", help="re-query Overpass before building")
    ap.add_argument("--strip-existing", action="store_true", help="drop contact tags from saved snapshots")
    a = ap.parse_args()
    if a.fetch:
        fetch()
    if a.strip_existing:
        for p in (REPAIR_FILE, DEALER_FILE):
            save_stripped(json.loads(p.read_text(encoding="utf-8")), p)
    build()

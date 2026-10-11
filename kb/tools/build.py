"""Validate the CarDoctor knowledge base and export it as one JSON file.

Usage:  python kb/tools/build.py        -> checks every CSV, writes kb/kb.json

Checks: every row cites at least one source that exists in sources.csv, every repair_type is in
repair_types.csv, urgency values come from the fixed scale, ids are unique, and prices carry a call date.
Exits with code 1 on any error so it can run in CI.
"""
import csv
import json
import sys
from pathlib import Path

KB = Path(__file__).resolve().parents[1]
URGENCY = {"stop_now", "fix_soon", "can_wait", "info"}
TABLES = {  # file -> id column
    "sources.csv": "source_id",
    "repair_types.csv": "repair_type",
    "visual_symptoms.csv": "symptom_id",
    "model_faults.csv": "fault_id",
    "workshops.csv": "workshop_id",
    "dealer_service_centres.csv": "dealer_id",
    "prices_template.csv": "price_id",
}


def read(name):
    with (KB / name).open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def split(v):
    return [x for x in (v or "").split(";") if x]


def main():
    data = {name[:-4]: read(name) for name in TABLES}
    errors = []
    sources = {r["source_id"] for r in data["sources"]}
    repair_types = {r["repair_type"] for r in data["repair_types"]}

    for name, id_col in TABLES.items():
        rows = data[name[:-4]]
        ids = [r[id_col] for r in rows]
        dupes = {i for i in ids if ids.count(i) > 1}
        if dupes:
            errors.append(f"{name}: duplicate ids {sorted(dupes)}")
        for r in rows:
            rid = r[id_col]
            if "source_ids" in r:
                cited = split(r["source_ids"])
                if not cited:
                    errors.append(f"{name}:{rid}: no source")
                errors += [f"{name}:{rid}: unknown source {s}" for s in cited if s not in sources]
            if "repair_types" in r:
                errors += [f"{name}:{rid}: unknown repair_type {t}" for t in split(r["repair_types"]) if t not in repair_types]
            if "urgency" in r and r["urgency"] not in URGENCY:
                errors.append(f"{name}:{rid}: bad urgency {r['urgency']!r}")
            if name == "prices_template.csv" and not r.get("date_called"):
                errors.append(f"{name}:{rid}: price without call date")

    if errors:
        print("\n".join(errors))
        sys.exit(1)
    data["meta"] = {
        "urgency_scale": ["stop_now", "fix_soon", "can_wait", "info"],
        "licence_note": "Workshop locations (c) OpenStreetMap contributors, ODbL 1.0. Other rows: our summaries of the cited sources.",
    }
    out = KB / "kb.json"
    out.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print("OK " + ", ".join(f"{k}={len(v)}" for k, v in data.items() if k != "meta") + f" -> {out}")


if __name__ == "__main__":
    main()

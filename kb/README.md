# CarDoctor knowledge base (T13)

Sourced data the CarDoctor engine retrieves from. **Every row cites a source id** from `sources.csv`; the LLM may only explain what these rows say.
Owner: Bexruz + `codex`. Built Sun 11 Oct 2026.

```bash
python kb/tools/build.py            # validate all CSVs, write kb/kb.json
python kb/tools/osm_workshops.py    # rebuild workshops.csv from the saved OSM snapshots (add --fetch to re-query)
```

## Files
| File | Rows | What it is | Used for |
|---|---|---|---|
| `visual_symptoms.csv` | 28 | Warning lights (16), leak colours (7), exhaust smoke colours (5): meaning, urgency, driver action | Labels for the visual library (vector DB #1); `label` = class name |
| `model_faults.csv` | 33 | Known faults of Nexia, Gentra, Lacetti, Spark, Cobalt, Damas, BYD Yuan Plus, BYD Song Plus: symptom (EN + RU), cause, mileage, repair | Text RAG (vector DB #2) |
| `repair_types.csv` | 17 | Shared vocabulary `repair_type` → which workshop categories can do it; labels EN/RU/UZ | Joins symptoms/faults to workshops |
| `workshops.csv` | 334 | Tashkent repair places from OpenStreetMap with lat/lon and category | Workshop map + matching |
| `dealer_service_centres.csv` | 5 | Official dealer service addresses from directories (mostly no coords yet) | Brand-only jobs (EV/HV, airbags) |
| `prices_template.csv` | 0 | Empty: filled **only** from our own phone calls, with date | Cost range |
| `sources.csv` | 16 | Every source: publisher, URL, date, language, reliability note | Citations in the answer |
| `kb.json` | – | All tables in one file (generated) | Easy loading |
| `raw/` | – | OSM snapshots (contact tags removed) | Reproducibility |

## Shared fields (proposed interface for T10)
- `urgency` ∈ `stop_now` · `fix_soon` · `can_wait` · `info` (UI: "stop driving now / fix this week / can wait / normal").
- `repair_types`: `;`-separated keys from `repair_types.csv`. A workshop matches when its `category` is in that repair type's `workshop_categories`; `brand_service` / `brand_dealer` match when `brands` contains the car's make.
- `source_ids`: `;`-separated keys from `sources.csv`.
- `model_faults.urgency_basis`: `source` = the source states the urgency; `team_rule` = our rule (safety items such as brakes, steering and fuel → `fix_soon` or higher; comfort or noise → `can_wait`). The rule is ours, not the source's — say so in the UI.

## Honest limits (say these in the pitch if asked)
- **Not failure statistics.** Model faults come from motoring journalists' reviews, recalls and complaint rankings, not from measured failure rates.
- **Generation mismatch.** Spark rows describe Spark II; Uzbek-built Spark is M300. Lacetti 1.6/1.8 engine rows do not apply to Gentra 1.5. US "Chevrolet Cobalt" (2005–2010, ignition-switch recall) is a **different car** from the Uzbek Cobalt. We left those US recalls out on purpose.
- **Damas:** we found no solid source on typical faults, only a 2009 Korea-only recall. Next step: interview 2–3 local mechanics.
- **BYD:** recalls are China-market; Uzbek cars must be checked by VIN at the dealer.
- **Workshops:** OSM coverage is incomplete; 110 places have no name; the category comes from name keywords (`category_basis` says which rule). Phone and e-mail tags are dropped on purpose (personal data). `verified_by_team = no` until someone checks.
- **Prices:** none yet. Filling them needs real calls to 3–5 shops per job. Never estimate them.

## Licences
- Workshop locations: © OpenStreetMap contributors, [ODbL 1.0](https://www.openstreetmap.org/copyright). `workshops.csv` and `raw/` are derived databases and stay under ODbL; attribution is required on the map.
- Other rows: our own short summaries of the cited articles (no copied text), with links in `sources.csv`.

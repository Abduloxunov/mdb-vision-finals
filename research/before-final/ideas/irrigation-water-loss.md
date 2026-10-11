---
title: Irrigation water-loss monitoring from satellite imagery
track: cv
status: inbox
added_by: Abduloxunov
date: 2026-09-19
tags: [remote-sensing, satellite, agriculture, water, government, sentinel-2]
---

# Irrigation water-loss monitoring

## One-liner
Free satellite imagery, processed every week, showing a water authority which fields are being
over-watered, which canal sections are leaking, and how many cubic metres each district is
losing — without installing a single sensor.

## Problem
- Agriculture consumes about **90% of Uzbekistan's water**.
- Measured **conveyance efficiency in the Zarafshan basin: 63–66%** — roughly **a third of the
  water never reaches a field**.
- **Kashkadarya, Surkhandarya and Bukhara** depend on Amu Darya inflows and face materially
  greater irrigation risk as summer demand peaks.
- The country is actively digitising irrigation infrastructure (sensors, automated canal
  controls, remote monitoring), but **sensors cover a tiny fraction of the network** and cost
  money per point.
- **The process being replaced:** manual field inspection and paper water-use reporting by
  mirab/WUA staff who cannot physically walk thousands of kilometres of canal.

## Solution
1. Pull **Sentinel-2** imagery (free, ~10 m resolution, revisit every ~5 days) for a district.
2. Segment fields and canals; classify crop type per field.
3. Compute vegetation and moisture indices (NDVI, NDWI, NDMI) per field per week.
4. Compare actual water status against **expected crop water requirement** for that crop and
   growth stage (CropWat-style model) → flag **over-watered** and **water-stressed** fields.
5. Detect **anomalous wet strips alongside canals** = likely leakage or unlined sections.
6. Output: a district map with a ranked list — "these 14 canal segments and 60 fields account
   for most of the estimated loss", with an estimated volume and cost.

## Why now / what's new
- Sentinel-2 is free and global, so **there is no data-collection problem at all** — we can
  process an entire province during the hackathon.
- Published work already computes **satellite-based crop water requirements for cotton and wheat
  in the Fergana Valley**, so the method is validated; the contribution is turning it into a
  usable operational tool.
- Segmentation foundation models (SAM 3) make field and canal delineation far easier than it was.

## Existing alternatives
- Research papers and international projects (IWMI and others) do this as studies, not as a tool
  a district officer can open on Monday morning.
- Commercial agri-analytics platforms exist but target large agribusiness, price in dollars per
  hectare, and are not tuned to Uzbek canal irrigation. `(unverified — check before claiming)`
- **Our positioning:** free data, a district-level operational dashboard, in Uzbek/Russian,
  measured in cubic metres and soʻm.

## Demo plan (2 days)
- Pick one real district (e.g. in Bukhara or Kashkadarya) and process a full season.
- Time slider across the season, so judges watch fields dry out and canals leak.
- Click a flagged canal segment → the raw imagery and the reason for the flag.
- Headline number on screen: **estimated m³ lost, and what that water is worth**.

## Data & tech
- Data: Sentinel-2 L2A via Copernicus/AWS open data; Sentinel-1 radar as a stretch (works
  through cloud); field boundaries from OpenStreetMap or segmentation.
- Models: segmentation (SAM 3 / U-Net) for fields and canals, plus index-based physical model —
  **deliberately not a black box**, which makes it defensible to an agronomist.
- Stack: Python, rasterio, geopandas, xarray, Leaflet or deck.gl for the map.
- Biggest risk: **validation**. We have no ground truth for actual water delivered. Mitigation:
  validate crop classification against known patterns, present loss figures as *estimates with
  stated assumptions*, and never overclaim precision.
- Second risk: this is heavy on geospatial plumbing; budget time for data wrangling, not modelling.

## Business
- Buyer: Ministry of Water Resources, basin irrigation authorities, Water User Associations,
  large farms, and donor projects (World Bank, ADB, IWMI) funding irrigation modernisation.
- Model: per-district annual subscription; cheaper than a single physical flow meter.
- Expansion: the same pipeline serves crop yield forecasting and pasture monitoring — both
  named government priorities.

## Score (1–5) — provisional
| Criterion | Weight | Score | Why |
|---|---|---|---|
| Innovation & Originality | 25% | 4 | Method known in research; operational local tool is not |
| Technical Complexity | 25% | 4 | Remote sensing + segmentation + physical model |
| Impact & Practicality | 25% | 5 | National water crisis, quantified in m³ |
| Presentation / demo-ability | 15% | 4 | Beautiful maps; less visceral than a live camera |
| Business Potential | 10% | 4 | Donor and ministry money already flowing here |
| **Weighted total** | | **4.25** | |

## Open questions
- Which district do we demo, and can we get any ground-truth water data for it?
- Cloud cover in the target season — do we need Sentinel-1 radar as backup?
- Can we reach a Water User Association for a five-minute reality check?

## Related
[[research-cv-landscape-sep-2026]] · [[global-ai-fintech-hackathon-cases]]

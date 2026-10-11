---
title: Illegal dumping detection and waste sorting
track: cv
status: inbox
added_by: Abduloxunov
date: 2026-09-19
tags: [environment, municipal, mapping, crowdsourcing, recycling]
---

# Illegal dumping detection / waste sorting

## One-liner
A camera on a bus or delivery van spots illegal rubbish dumps along the route, maps them by GPS,
tracks whether they grow or get cleared, and gives the city a ranked cleanup list instead of
complaint phone calls.

## Problem
- Illegal dumping appears faster than anyone reports it; the city learns about a dump when a
  resident complains, by which point it has grown.
- No one knows **which sites recur**, so the same corner is cleaned repeatedly while the cause is
  never addressed.
- Separately, recycling fails at the sorting step: people do not know which bin an item belongs in.
- **The process being replaced:** citizen complaint calls and manual inspection rounds.

## Solution
**Two products from one model; pick one for the hackathon.**

**A. Dumping detection and mapping (recommended)**
1. A phone or dashcam on a regularly moving vehicle (bus, taxi, delivery van) records the street.
2. Detect waste piles and construction debris; classify size and type.
3. GPS-tag, deduplicate across passes, and track each site over time: new, growing, shrinking,
   cleared.
4. Municipal dashboard: ranked cleanup list, recurrence heat map, and a measure of how long sites
   stay uncleared after reporting — an accountability metric a city can be judged on.

**B. Waste sorting assistant**
Point the phone at an item and get the correct bin, with the reasoning, and a local recycling
point on a map.

## Why now / what's new
- Zero-shot detection handles the long tail of "rubbish" without labelling every kind of debris.
- Any vehicle that already drives a fixed route becomes a sensor, so coverage costs nothing.
- The **time dimension** (does a site come back after cleaning?) is what nobody does and what
  makes this a municipal management tool rather than a photo classifier.

## Existing alternatives
- Citizen complaint apps and hotlines: reactive, and depend on someone bothering to report.
- Some cities abroad run camera-based dumping detection on refuse trucks. `(unverified)`
- **Our positioning:** passive collection from existing vehicles, plus recurrence tracking and
  accountability metrics.

## Demo plan (2 days)
- Drive a route in Tashkent with a phone on the windscreen, and process the footage.
- Show detections appearing as pins on the map, live from our own footage.
- Show the same site across two passes — grown, or cleared — because that comparison is the story.
- Hand the judges the ranked cleanup list for a district.

## Data & tech
- Data: our own street footage (a couple of hours' driving); public waste datasets (TACO and
  similar) for pretraining. `(verify licences)`
- Models: RF-DETR or YOLO26 fine-tuned on waste piles, plus zero-shot for the long tail; simple
  geospatial clustering for deduplication.
- Stack: Python, OpenCV, GPS logging, a map dashboard.
- **Biggest risk: originality.** Waste detection is a very common hackathon project. Everything
  distinctive here is in the recurrence tracking and the municipal workflow, so lead with those.
- Second risk: GPS drift of several metres means sites must be clustered by radius, not exact point.

## Business
- Buyers: city administration, district khokimiyats, waste management contractors, and
  environmental agencies.
- Model: per-city subscription; contractors pay for route optimisation; the accountability metric
  is what sells it to a mayor.
- Cheap to deploy since no new hardware is needed beyond phones already in vehicles.

## Score (1–5) — provisional
| Criterion | Weight | Score | Why |
|---|---|---|---|
| Innovation & Originality | 25% | 2 | Very common theme; recurrence tracking is the only fresh angle |
| Technical Complexity | 25% | 3 | Detection + geospatial dedup + time series |
| Impact & Practicality | 25% | 3 | Visible city problem, clear buyer |
| Presentation / demo-ability | 15% | 4 | Local footage is relatable |
| Business Potential | 10% | 3 | Municipal budgets are slow but real |
| **Weighted total** | | **2.8** | |

**Recommendation:** weakest of the batch. Keep as a fallback unless we find a local partner
(a district khokimiyat or a waste contractor) willing to say they would use it.

## Open questions
- Can we get a letter of interest from any district administration before the finals?
- Bus/taxi fleet partner for footage?
- Does the city already have dumping-site data we could validate against?

## Related
[[research-cv-landscape-sep-2026]]

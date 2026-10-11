---
title: Bazaar produce scanner — quality grading and fair-price estimate
track: cv
status: inbox
added_by: Abduloxunov
date: 2026-09-19
tags: [retail, agriculture, fine-grained, consumer, local, crowdsourcing]
---

# Bazaar produce scanner

## One-liner
Point your phone at a crate of tomatoes at Chorsu: the app names the variety, grades the quality,
estimates today's fair price from what others paid nearby, and tells you whether you are being
overcharged.

## Problem
- Bazaar pricing is opaque: the same produce costs different amounts to different buyers on the
  same day, and quality is judged by eye and argument.
- Buyers (households, restaurants, small shops) have **no reference price** and no way to assess
  quality objectively.
- Farmers and wholesalers have the mirror problem: no visibility into where their produce grades
  and prices out.
- **The process being replaced:** haggling from ignorance, and manual visual grading of produce.

## Solution
1. Photograph the produce.
2. **Classify** type and variety (tomato vs. which tomato).
3. **Grade quality** from visual features: size uniformity, colour ripeness, blemishes, bruising,
   mould, wilting. Output a grade with the reasons visible.
4. **Price:** combine grade with crowd-collected recent prices (users confirm what they paid,
   tagged by market and date) → a fair-price band for today.
5. Over time this becomes a **live produce price and quality index** for Uzbek markets, which is
   a genuinely valuable dataset that does not currently exist.

## Why now / what's new
- Fine-grained visual grading used to need per-crop labelled datasets; a small VLM fine-tuned on a
  few hundred photos now gets usable results.
- Everyone in the market already has a phone, so the crowdsourcing loop is feasible.
- Nobody has built a produce price index for Uzbekistan from images. `(unverified)`

## Existing alternatives
- Industrial produce-grading machines exist for packhouses (expensive, fixed installations).
- Price-comparison apps exist for supermarkets, not bazaars.
- **Our positioning:** the bazaar, in the buyer's hand, where most food in the country is actually
  bought.

## Demo plan (2 days)
- **Bring real fruit and vegetables to the judging table.** Judges hold up a tomato, we grade it
  live and explain why.
- Show two crates side by side — one good, one poor — and the grades matching intuition.
- Show the price map built from data we collected at a real bazaar during the hackathon.

## Data & tech
- Data: our own photos from Chorsu/Alay markets, with grades labelled by consensus (and ideally
  with a vendor's opinion as ground truth); price notes collected at the same time.
- Models: classification + fine-grained grading (fine-tuned small VLM or CNN); simple statistics
  for the price band.
- Stack: Python, phone web app, a small map view.
- **Biggest risk: the price half is crowdsourcing, not vision.** With no users there is no price
  data, so the demo must lean on the grading, with prices from what we collected ourselves.
- Second risk: "quality" is subjective — define the grading rubric explicitly and show it.

## Business
- Buyers: restaurants and shops buying in bulk (consistent quality matters to them), wholesalers,
  and eventually the price index itself sold to analysts, retailers or statistics agencies.
- Consumer app free, drives data; B2B sells the index and grading API.

## Score (1–5) — provisional
| Criterion | Weight | Score | Why |
|---|---|---|---|
| Innovation & Originality | 25% | 3 | Produce grading is well-trodden; the bazaar index is the fresh part |
| Technical Complexity | 25% | 3 | Fine-grained classification, modest pipeline |
| Impact & Practicality | 25% | 3 | Real but low-stakes problem |
| Presentation / demo-ability | 15% | 5 | Physical, fun, judges participate |
| Business Potential | 10% | 3 | Index has value; consumer monetisation is weak |
| **Weighted total** | | **3.3** | |

## Open questions
- Which crop do we demo (one done well beats five done badly)?
- Will vendors let us photograph and ask prices, and do we need permission?
- Is there existing official price data we can validate against?

## Related
[[research-cv-landscape-sep-2026]]

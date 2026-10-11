---
title: Livestock counting, identity and health monitoring from video
track: cv
status: inbox
added_by: Abduloxunov
date: 2026-09-19
tags: [agriculture, drone, tracking, re-identification, lending, pasture]
---

# Livestock monitoring

## One-liner
Fly a drone (or walk with a phone) over a flock, and get a verified head count, individual
animal identities, and a flag on any animal that is limping or behaving abnormally — turning
livestock into an asset a bank can actually lend against.

## Problem
- **Counting is manual, slow and disputed.** A farmer with 500 sheep counts them by eye; so does
  the buyer, the insurer and the loan officer, and they disagree.
- **Livestock is the main household asset in rural Uzbekistan, but it is poor collateral** because
  a lender cannot verify that the animals exist today, or that the same 500 sheep were not shown
  to three different banks. `(unverified — confirm with a rural bank before pitching)`
- **Health problems are caught late.** Lameness and illness show in gait and behaviour days
  before a farmer notices, and by then the animal has lost weight or infected others.
- **Pasture monitoring is a stated government CV priority.**
- **The process being replaced:** manual head counts, paper livestock registers, and a vet's
  occasional visit.

## Solution
1. **Count:** detection + tracking over a drone or phone video; deduplicate across frames so a
   moving animal is counted once. Output a count with a confidence interval and the video as proof.
2. **Identify:** re-identification from coat pattern, ear tag or muzzle, so the same animal is
   recognised across visits. This is what makes verification meaningful.
3. **Health:** gait analysis from tracked motion → flag lameness; flag animals that separate from
   the group or stop moving, both classic early illness signs.
4. **Record:** a timestamped, geotagged, signed report a bank or insurer can rely on.

## Why now / what's new
- **SAM 3** tracks every instance of a concept across video from a text prompt, and **SAM 3.1**
  adds multi-object tracking at scale (reported ~7× faster at 128 objects) — dense flock tracking
  is exactly the case that was impractical before. `(unverified — test on real flock video)`
- Zero-shot detectors mean an initial demo needs **no labelled data at all**.
- Consumer drones are cheap and widely available.

## Existing alternatives
- Ear tags and RFID: the official approach, but they cost per animal, get lost, and still require
  someone to physically scan each animal.
- Western precision-livestock platforms exist for indoor cattle barns, not open pasture flocks of
  sheep. `(unverified)`
- **Our positioning:** no hardware on the animal, works on a flock in open pasture, and produces
  a verifiable record rather than just a number.

## Demo plan (2 days)
- Film a real flock near Tashkent (this is a weekend job, and the footage is our moat).
- On stage: play the video, watch boxes lock on, and the counter settle on a number.
- Judge picks an animal on screen → the system shows it again in a second clip filmed later.
- Flag the limping animal in a prepared clip and explain the gait signal.

## Data & tech
- Data: our own drone/phone footage; public animal detection datasets for pretraining.
- Models: detection (RF-DETR / YOLO26) + tracking (SAM 3 / ByteTrack) + a simple re-ID embedding;
  gait from tracked keypoints.
- Stack: Python, OpenCV, supervision; a phone app or web upload for the demo.
- Biggest risk: **occlusion in dense flocks** — animals overlap constantly and counts drift.
  Mitigation: count at a choke point (a gate or a narrow path), which is how farmers count anyway,
  and present that as a deliberate design choice.
- Second risk: re-ID on sheep is genuinely hard (they look alike). Demo it on cattle if sheep fail.

## Business
- Buyers: banks and microfinance (collateral verification), insurers, large farms, veterinary
  services, and government livestock registries.
- Model: per-verification fee for lenders, plus a subscription for farms.
- The lending angle is the strongest business story on our whole idea list: it unlocks credit for
  rural households using an asset they already own.

## Score (1–5) — provisional
| Criterion | Weight | Score | Why |
|---|---|---|---|
| Innovation & Originality | 25% | 4 | Counting is common; identity + credit verification is not |
| Technical Complexity | 25% | 4 | Tracking, re-ID, dedup, gait |
| Impact & Practicality | 25% | 4 | Rural incomes, credit access, animal health |
| Presentation / demo-ability | 15% | 5 | Drone footage on a big screen is unbeatable visually |
| Business Potential | 10% | 4 | Clear per-verification revenue from lenders |
| **Weighted total** | | **4.15** | |

## Open questions
- Can we get access to a flock and a drone this month?
- Cattle or sheep for the re-ID demo?
- Does any bank here already lend against livestock, and how do they verify it today?

## Related
[[research-cv-landscape-sep-2026]] · [[irrigation-water-loss]]

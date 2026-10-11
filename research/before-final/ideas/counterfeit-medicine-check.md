---
title: Counterfeit medicine and product verification from a phone photo
track: cv
status: inbox
added_by: Abduloxunov
date: 2026-09-19
tags: [health, anti-counterfeit, fine-grained, consumer, pharma]
---

# Counterfeit medicine check

## One-liner
Before you swallow it, photograph the box: the app compares print quality, fonts, holograms,
colour and batch markings against the manufacturer's genuine reference and tells you in two
seconds whether this packet looks real.

## Problem
- Counterfeit and substandard medicines circulate in the region; a patient, a pharmacist or a
  small clinic has **no practical way to check a packet** beyond intuition.
- Consequences are severe: an ineffective antibiotic or a fake cardiac drug kills quietly and
  is never traced back.
- Existing defences (holograms, serial codes) only work if someone verifies them, and verification
  today means typing a code into an SMS service — slow, and easily faked by printing valid-looking
  codes. `(unverified — check whether Uzbekistan runs a national drug-verification scheme)`
- **The process being replaced:** a pharmacist's eyeball judgement, or nothing at all.

## Solution
1. Photograph the box (and optionally the blister).
2. Identify the product from packaging text and layout (OCR + matching) — reuse of the work in
   [[uzbek-document-ocr]].
3. **Fine-grained comparison** against a stored genuine reference: font shapes and spacing, print
   registration and dot pattern, colour profile under the phone's flash, hologram behaviour across
   two frames at different angles, embossing and cut edges.
4. Verdict with reasons: "font on the dosage line differs; batch code font inconsistent" — never
   just a score. Explanations are what make it trustworthy and what impress judges.
5. Report suspicious findings with location, building a live map of where fakes appear.

## Why now / what's new
- Small VLMs can describe fine visual differences and generate the human-readable explanation,
  which is the hard part of the UX.
- Phone cameras and flash are good enough to capture print texture at macro distance.
- Fine-grained visual comparison (same object class, tiny differences) is a genuinely hard CV
  problem, which is good for the Technical Complexity score.

## Existing alternatives
- Serial-code SMS/app verification schemes, track-and-trace systems, and manufacturer hotlines:
  all rely on codes, not on the physical artefact.
- Global anti-counterfeit vision products exist, typically sold to brands rather than consumers.
  `(unverified)`
- **Our positioning:** consumer-side, works offline on the packet in your hand, and explains its
  reasoning.

## Demo plan (2 days)
- A tray of medicine boxes on the judges' table: some genuine, some altered by us (we print a
  modified box with a slightly wrong font or colour).
- Judge picks any box, photographs it, and gets a verdict with highlighted differences.
- Show the heat map of *what* differed on the packaging.
- Be explicit that our fakes are simulated, and say exactly how we made them.

## Data & tech
- Data: photos of genuine packaging we buy ourselves (many angles, lighting, wear) plus
  **simulated counterfeits** we print with deliberate deviations.
- Models: OCR/text matching for identification; a siamese or metric-learning network for
  genuine-vs-suspect comparison; a VLM for the explanation text.
- Stack: Python, PyTorch, a phone camera web app.
- **Biggest risk: we have no real counterfeits.** A model trained only on our simulated fakes may
  learn our printer, not counterfeiting. Mitigation: be transparent, frame it as anomaly detection
  against the genuine reference (one-class), and say plainly what would be needed to validate it
  properly. Judges reward this honesty; pretending otherwise gets punished in Q&A.
- Second risk: legal and reputational sensitivity — never name a real manufacturer as counterfeit
  on stage.

## Business
- Buyers: pharmaceutical manufacturers protecting their brand, pharmacy chains, the drug
  regulator, and hospital procurement.
- Model: brands pay to have their packaging fingerprinted and monitored; the consumer app is free
  and generates the field data.
- Same technology extends to spare parts, cosmetics, alcohol and luxury goods.

## Score (1–5) — provisional
| Criterion | Weight | Score | Why |
|---|---|---|---|
| Innovation & Originality | 25% | 4 | Fine-grained anomaly detection on packaging, consumer-side |
| Technical Complexity | 25% | 4 | Metric learning, fine detail, explanations |
| Impact & Practicality | 25% | 4 | Health risk, but hard to validate in 2 days |
| Presentation / demo-ability | 15% | 5 | Judges physically test it with boxes in their hands |
| Business Potential | 10% | 4 | Brands already spend on anti-counterfeiting |
| **Weighted total** | | **4.15** | |

## Open questions
- Does Uzbekistan already run a national drug-verification system we would duplicate?
- Can a pharmacist tell us which products are actually faked here?
- Is one-class anomaly detection enough, or do we need real counterfeit samples to be credible?

## Related
[[uzbek-document-ocr]] · [[research-cv-landscape-sep-2026]]

---
title: Privacy-preserving construction and workplace safety monitoring
track: cv
status: inbox
added_by: Abduloxunov
date: 2026-09-19
tags: [safety, zero-shot, privacy, edge, construction, government]
---

# Construction / workplace safety monitoring

## One-liner
An existing site camera plus a cheap edge box detects safety violations — no helmet, person in
an exclusion zone, no harness at height — and sends the supervisor an alert with faces blurred
on the device, so no worker is ever surveilled personally.

## Problem
- Construction is among the most dangerous sectors, and violations are found **after** the
  accident, from footage nobody was watching live.
- **Violation detection on construction sites and in industry is an explicitly stated government
  CV priority** in Uzbekistan, alongside production monitoring via video analytics.
- Sites already have cameras; what they lack is anyone watching 30 feeds at once.
- **The process being replaced:** a safety officer walking the site, or reviewing recordings after
  an incident.

## Solution
1. Connect to existing RTSP camera streams.
2. **Zero-shot detection** of violations described in plain text: "worker without a hard hat",
   "person inside the crane exclusion zone", "no high-visibility vest".
3. Zone rules drawn on the camera image (danger zone, no-entry, height area).
4. **Privacy by design:** faces blurred on the edge device, only the violation event leaves
   (crop + timestamp + zone), and raw video never goes to the cloud.
5. Alert to the supervisor's phone/Telegram in seconds, plus a weekly report showing which zones
   and shifts produce the most violations.

## Why now / what's new
- **Grounding DINO and YOLO-World detect from a text prompt with no training**, so new rules are
  added by typing a sentence instead of labelling 5,000 images. That is the whole product story:
  a safety officer can add a rule themselves.
- Edge AI is now the default for real-time vision, so this runs on a cheap box on site with no
  bandwidth bill.

## Existing alternatives
- Several international PPE-detection products exist (this is a crowded space globally) and are
  priced per camera per month in dollars. `(unverified)`
- Most require a labelled dataset per new rule and send video to the cloud, which is exactly the
  objection site owners raise.
- **Our positioning:** text-defined rules, on-premise, privacy-preserving, affordable locally.

## Demo plan (2 days)
- Live: a teammate walks in front of a laptop camera with and without a hard hat, and the alert
  fires on screen and in Telegram.
- Type a **new rule live in front of the judges** — "person carrying a ladder" — and have it work
  without retraining. This is the moment that wins the demo.
- Show the blurred output to prove the privacy claim.
- Weekly report view with violations by zone and by hour.

## Data & tech
- Data: **none needed to start** (zero-shot); optionally fine-tune on a public PPE dataset for
  accuracy numbers.
- Models: YOLO-World / Grounding DINO for open-vocabulary detection; a tracker to avoid alerting
  40 times for the same person; face detection + blur on-device.
- Stack: Python, OpenCV, RTSP, a small dashboard, Telegram bot for alerts.
- Biggest risk: **low originality** — PPE detection is a standard demo. The zero-shot rule editor
  and the privacy architecture are what make it defensible; lead with those, not with helmets.
- Second risk: false alarms destroy trust. Show the confidence threshold and an easy "not a
  violation" feedback button.

## Business
- Buyers: construction companies, factories, mining and oil/gas contractors, and insurers who
  price site risk.
- Model: per-camera monthly subscription; the edge box is a one-off cost.
- Regulatory tailwind: if the state pushes violation detection, compliance becomes the sales pitch.

## Score (1–5) — provisional
| Criterion | Weight | Score | Why |
|---|---|---|---|
| Innovation & Originality | 25% | 3 | Crowded space; the rule editor + privacy angle carry it |
| Technical Complexity | 25% | 3 | Mostly assembly of existing models |
| Impact & Practicality | 25% | 4 | Lives, plus a stated state priority |
| Presentation / demo-ability | 15% | 5 | Live, interactive, judges can test it themselves |
| Business Potential | 10% | 4 | Clear per-camera pricing, existing global market |
| **Weighted total** | | **3.55** | |

## Open questions
- Can we get access to a real site camera feed, even for one afternoon?
- Which single rule matters most to a local contractor — helmets, zones or heights?
- Is there a local safety regulation we can name in the pitch?

## Related
[[research-cv-landscape-sep-2026]]

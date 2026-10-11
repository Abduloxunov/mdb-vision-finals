---
title: Real-time sign language translator (RSL / Uzbek deaf community)
track: cv
status: inbox
added_by: Abduloxunov
date: 2026-09-18
tags: [accessibility, video, pose, sequence-models, social-impact]
---

# Real-time sign language translator

## One-liner
A phone or laptop app that watches a signer through the camera and turns their signs into
spoken and written Uzbek in real time (and back), so deaf people can be understood at a
clinic reception, a bank counter or a government service desk without a human interpreter.

## Problem
- Deaf and hard-of-hearing people depend on a small number of human interpreters for any
  interaction with hospitals, banks, police, universities or public services.
- Interpreters must be booked in advance, cost money, and are unavailable outside working
  hours or in the regions — so routine errands become blocked or humiliating.
- **To verify before the finals:** number of deaf / HoH people in Uzbekistan, number of
  certified interpreters, which sign language is used in practice (Russian Sign Language
  is widely used across the post-Soviet space; a distinct local variant may exist). Sources
  needed — ask the deaf community association directly, do not guess. `(unverified)`

## Solution
Camera → hand/body/face landmarks → sequence model → text → speech.
1. **Landmarks:** MediaPipe Holistic (hands + pose + face) or a pose estimator, giving a
   compact feature vector per frame instead of raw pixels — fast, and robust to background.
2. **Sequence model:** Bi-LSTM / GRU / small Transformer over the landmark sequence to
   classify a sign, then stitch signs into phrases.
3. **Output:** text on screen + TTS voice; reverse direction = speech-to-text + a signing
   avatar or clip playback.
4. Everything runs **on device** — no video leaves the phone, which matters for medical and
   banking settings.

## Why now / what's new
- Real-time pose and hand landmarks now run at 30 fps on a phone CPU.
- Landmark-based sequence models train on **small datasets** — a team can record its own
  vocabulary in days, which is exactly what a hackathon allows.
- A real-time Ukrainian Sign Language translator using computer vision + Bi-LSTM (for
  clinics, schools and public services) was a hackathon winner in 2026 — proof the format
  reads well to judges. See [[research-cv-landscape-sep-2026]].
- Small VLMs on-device open a stretch goal: describing context, not just isolated signs.

## Existing alternatives
- Global research prototypes and a few commercial apps exist for ASL; quality drops sharply
  for low-resource sign languages.
- **No known productised RSL / Uzbek solution** — the gap is the opportunity. `(unverified)`
- Human interpreter services and video relay: the real competitor, and our benchmark for
  cost and speed.

## Demo plan (what works on stage in 2 days)
- Live camera demo: a judge (or a deaf guest) signs 20–40 practical signs — "help",
  "doctor", "pain", "passport", "how much", digits — and the laptop speaks them out loud.
- A scripted scenario: a pharmacy counter conversation, end to end, both directions.
- Latency counter on screen, and a visible "runs offline" airplane-mode moment.
- **Strongest possible move:** invite a member of the deaf community to test it live on stage.

## Data & tech
- Data: our own recorded vocabulary (3 team members × N repetitions × M signs), plus any
  public RSL video we can find. Augment by mirroring, speed and landmark jitter.
- Models: MediaPipe Holistic → Bi-LSTM / small Transformer; TTS for Uzbek output.
- Stack: Python + OpenCV for the prototype, then a phone or web app for the demo.
- Biggest technical risk: **continuous** signing (where one sign ends and the next begins)
  is much harder than isolated signs. Mitigation: demo isolated + short phrases, and be
  honest in the pitch about the roadmap.

## Business
- Buyers: banks and telecom branches (accessibility compliance), hospitals and clinics,
  public service centres, universities.
- Model: per-branch licence or per-device subscription; a free consumer app for the
  community drives adoption and goodwill.
- Wider market: the same pipeline retargets to any sign language by swapping the dataset.

## Score (1–5 each) — provisional, revisit after research
| Criterion | Weight | Score | Why |
|---|---|---|---|
| Innovation & Originality | 25% | 4 | Method is known; applying it to RSL/Uzbek is not |
| Technical Complexity | 25% | 4 | Real-time multi-stage pipeline, sequence modelling |
| Impact & Practicality | 25% | 5 | Clear, human, locally underserved |
| Presentation / demo-ability | 15% | 5 | Live, emotional, instantly understandable on stage |
| Business Potential | 10% | 3 | Real buyers, but accessibility budgets are thin |
| **Weighted total** | | **4.3** | |

## Open questions
- Which sign language do deaf Uzbeks actually use day to day?
- Can we reach the deaf community association before the finals for advice and testers?
- Is there any public RSL video dataset with a usable licence?

---
title: Privacy-first classroom attendance and exam integrity
track: cv
status: inbox
added_by: Abduloxunov
date: 2026-09-19
tags: [education, privacy, on-device, university, wiut]
---

# Classroom attendance / exam integrity

## One-liner
One camera at the front of the lecture hall marks attendance for 200 students in three seconds,
without storing a single face — the image never leaves the device and only a list of student IDs
comes out.

## Problem
- Attendance is taken by passing a sheet around or calling names, which wastes 5–10 minutes of
  every class and is trivially faked by a friend signing for you.
- At exam time, invigilation is labour-intensive, and online exams are hard to supervise fairly.
- Universities need attendance records for regulations, scholarships and visa compliance.
- **The process being replaced:** the paper register and the roll call.

## Solution
1. A camera at the front of the room captures one frame at the start of class.
2. Face detection + recognition against the enrolled cohort, **entirely on-device**.
3. Output is only a **list of student IDs present** — the frame and every embedding are discarded
   immediately, so there is no face database to leak or abuse.
4. Anti-spoofing: a photo of a friend's face on a phone screen is rejected (liveness/texture check).
5. Exam mode: detect anomalies (phone visible, a person entering or leaving, an empty seat where a
   student was) and log timestamped events for the invigilator to review, rather than making
   accusations automatically.

## Why now / what's new
- Face recognition on-device is fast and accurate enough on ordinary hardware.
- The **privacy architecture is the actual contribution**: most deployed systems upload faces to
  a server, which is precisely why students and regulators resist them.
- WIUT is the customer and is in the room, which is a rare advantage.

## Existing alternatives
- Commercial attendance systems (card readers, fingerprint scanners, cloud face recognition) —
  cards get passed around, fingerprints are slow in a queue, and cloud face recognition creates a
  biometric database nobody wants to own.
- Online proctoring services, widely disliked for exactly the surveillance reasons we avoid.
- **Our positioning:** no biometric database, no cloud, no per-student hardware.

## Demo plan (2 days)
- Run it on the judges: enrol 5 people in 30 seconds, then mark "attendance" from one photo.
- Try to fool it with a photo on a phone and show the spoof rejected.
- Show the storage folder afterwards, **empty**, to prove nothing was kept.
- Show the exported attendance record in the format a registrar would use.

## Data & tech
- Data: a few photos per enrolled person, captured at enrolment; no external dataset required.
- Models: a face detector plus a face-embedding model (both pretrained), a liveness check, and
  cosine matching against enrolled embeddings held encrypted.
- Stack: Python or a browser app with on-device inference; a small registrar-facing export.
- **Biggest risk: originality.** This is one of the most common student projects in the world.
  Without the privacy architecture and anti-spoofing it scores 2/5 on innovation.
- Second risk: **ethics questions in Q&A are guaranteed** — consent, opt-out, accuracy across
  skin tones and with hijab or glasses. Have honest answers ready; this is a chance to impress,
  not a trap, but only if prepared.

## Business
- Buyers: universities, schools, training centres, and corporate training compliance.
- Model: per-room licence; far cheaper than turnstiles or biometric hardware.
- Expansion: the same privacy-first pattern applies to any workplace attendance.

## Score (1–5) — provisional
| Criterion | Weight | Score | Why |
|---|---|---|---|
| Innovation & Originality | 25% | 2 | Very common project; privacy design is the only differentiator |
| Technical Complexity | 25% | 3 | Mostly assembly; liveness adds some depth |
| Impact & Practicality | 25% | 3 | Saves time, but low stakes |
| Presentation / demo-ability | 15% | 5 | Judges are the demo, and the spoof test is memorable |
| Business Potential | 10% | 3 | Real but crowded market |
| **Weighted total** | | **2.95** | |

**Recommendation:** weakest of the batch on innovation. Keep it as a backup, or fold the
privacy-first on-device pattern into a stronger idea such as [[construction-safety]].

## Open questions
- Would WIUT actually pilot it, and can we get that statement in writing before the finals?
- Accuracy in a dim lecture hall at the back row?
- What does local law say about biometric processing, even when nothing is stored?

## Related
[[construction-safety]] · [[research-cv-landscape-sep-2026]]

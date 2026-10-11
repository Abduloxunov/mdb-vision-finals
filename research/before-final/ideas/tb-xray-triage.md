---
title: TB screening triage — ranking chest X-rays where there is no radiologist
track: cv
status: inbox
added_by: Abduloxunov
date: 2026-09-19
tags: [medical-imaging, triage, public-health, offline, government]
---

# TB X-ray triage

## One-liner
A mobile TB screening van shoots 200 chest X-rays a day in a district with no radiologist on
site; our software reads them offline, ranks them by urgency, and tells the nurse which 12
people must not go home today.

## Problem
- Uzbekistan's National TB Strategy (2021–2026) targets a **50% cut in TB incidence** and a
  **75% cut in deaths**.
- USAID has handed **portable AI-equipped X-ray machines** to the National TB Program; each unit
  can take **~200 images per day**.
- The bottleneck is not imaging, it is **reading**: severe radiologist shortages in
  resource-limited areas mean missed pulmonary TB cases. Screening produces a pile of images
  nobody has time to interpret; results come back days later, by which time the patient has
  moved on.
- **The process being replaced:** a radiologist manually reading a queue of screening films —
  or, in practice, nobody reading them promptly at all.

## Solution
**Not a diagnosis. A triage queue.**
1. Ingest the day's X-rays (DICOM or JPEG) from the van's machine.
2. Classifier scores each image for TB-suggestive abnormality, with a heatmap showing *where*.
3. Sort the day's batch into **Urgent / Review / Likely normal**, with a confidence figure.
4. Nurse-facing screen: "these 12 need sputum testing before they leave", with the heatmap shown
   so a human can sanity-check every call.
5. Everything runs **offline on a laptop**; results sync to the central TB registry when the van
   regains connectivity.
6. Log every decision for later audit by a radiologist — this is what makes it deployable in a
   real health system.

## Why now / what's new
- Public TB chest X-ray datasets are open and well labelled: **Shenzhen**, **Montgomery**,
  **TBX11K** `(verify licences before use)`.
- Modern backbones fine-tune on a few thousand images on one consumer GPU.
- WHO-endorsed CAD products exist, which **proves the clinical concept** — our contribution is
  the offline, workflow-level layer around it, not the classifier itself.

## Existing alternatives
- **CAD4TB, qXR, Lunit INSIGHT CXR** — commercial, WHO-recognised CAD products already used in
  screening programmes. Do **not** claim to beat them; we will not, in two days.
- **Our positioning:** the gap is the **workflow**: batch triage, offline operation in a van,
  a nurse-readable queue, audit trail, and sync to the registry. Licences for the commercial
  tools are also expensive per site. `(unverified — check pricing before claiming)`

## Demo plan (2 days)
- Load a folder of 200 test X-rays live; the queue sorts itself in front of the judges.
- Click one flagged case → heatmap overlay + "why this was flagged".
- Airplane mode: it keeps working, then syncs when the network returns.
- Show the metric that matters: **how many minutes of radiologist time saved per 200 images**,
  and the sensitivity/specificity on our held-out test set.

## Data & tech
- Data: Shenzhen + Montgomery + TBX11K; hold out a clean test set and report honestly.
- Models: a standard image classifier (ConvNeXt/EfficientNet class) with Grad-CAM for heatmaps;
  a VLM is unnecessary and harder to defend clinically.
- Stack: Python, PyTorch, pydicom, a small local web UI.
- **Biggest risk: medical framing.** Say "triage support", never "diagnosis". A judge from a
  medical background will test this in the Q&A.
- Second risk: class imbalance and dataset bias — models trained on these datasets often learn
  the *scanner*, not the disease. Mention this yourself before a judge does.

## Business
- Buyer: the National TB Program, oblast health departments, donor programmes (USAID, Global
  Fund), private clinic chains.
- Model: per-site licence or per-study fee; on-prem only, since patient images cannot leave.
- Expansion: the same triage shell works for pneumonia, silicosis and routine screening.

## Score (1–5) — provisional
| Criterion | Weight | Score | Why |
|---|---|---|---|
| Innovation & Originality | 25% | 4 | The classifier is standard; the offline triage workflow is the novelty |
| Technical Complexity | 25% | 4 | Solid pipeline, calibration, explainability |
| Impact & Practicality | 25% | 5 | National priority, lives, an existing deployed fleet of machines |
| Presentation / demo-ability | 15% | 4 | Clear, serious, easy to follow |
| Business Potential | 10% | 4 | Named buyer with donor funding |
| **Weighted total** | | **4.3** | |

## Open questions
- Can we talk to anyone in the National TB Program before the finals?
- Which format do the donated machines output, and can we read it?
- Licences on TBX11K and the others for a competition demo?
- Do we have a medic or medical student who can sanity-check our language?

## Related
[[research-cv-landscape-sep-2026]] · [[global-ai-fintech-hackathon-cases]]

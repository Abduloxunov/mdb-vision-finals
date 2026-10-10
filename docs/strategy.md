# Strategy — idea, architecture, plan

Source: the team's strategy document (`WIUT_Hackathon_2026_Computer_Vision_Strategy_RU.docx`) and the "RoadGuard AI" concept poster, both shared by Muhammadjon on Sat 10 Oct.
Condensed and translated by claude-2. **Status: proposal — the lead (Davlatyor) confirms the final choice.**

> ⚠️ The poster is an AI-generated concept image. Its numbers (18.7 FPS, 52 ms, ~5,000-frame test set, $0.01–0.03 per frame, "$5–15K pilot", "6–12 months payback") were **not measured**. Do not put them in the deck or README: invented metrics are a disqualification item. Only numbers we measure ourselves go in.

## 1. Decision

| | |
|---|---|
| **Product** | **RoadProof** (the poster calls the wider platform *RoadGuard AI*; pick one name for slide 1) |
| **Mode** | **Startup** |
| **One-liner** | From road images to actionable maintenance evidence. |
| **What it does** | Road photo → quality check → road-damage detection → transparent priority → inspection report. A human inspector confirms the decision. |
| **User / payer** | Road maintenance service, city (hokimiyat) road department, fleet operator. The organisation that inspects roads pays. |
| **Fallback** | **LensCheck**: quality and completeness check for vehicle-inspection photos (sharpness, exposure, duplicates, required angles), done with OpenCV. Switch to it if no usable damage detector runs by **T+2h**. |
| **Principle** | A narrow product that works, with honest measurements, beats a broad platform with mocked features. |

**Why RoadProof:** public data exists (RDD2022, pothole sets), the live demo is easy to understand (the jury uploads any road photo), quality can be measured on our own test set, and the chain from image to action is real.
**Main risk:** weak transfer to local roads, rain and night. Never claim industrial reliability without a local test.

**Not in the MVP** (these appear on the poster, but in 23 h they would be mock screens): driver drowsiness, plate OCR, car damage, motorcycle safety, Jetson edge deployment. They can appear only under "Next steps".

## 2. Architecture

```
image upload (JPG/PNG, or a frame from a video)
   └─> 1. quality gate      size, blur (variance of Laplacian), brightness/exposure, "is this a road?" → reject with a reason
   └─> 2. CV inference      road-damage detector → class, bbox, confidence
   └─> 3. decision engine   transparent rules: class severity × confidence × area share → priority (low/medium/high) + reasons
   └─> 4. report            original image + boxes, quality result, priority, limitations, recommended action
   └─> 5. log               JSONL/SQLite row per request (for metrics, latency, cost)
```

- Model confidence is **not** a crash probability and **not** a measured severity.
- We do **not** measure pothole depth or area in physical units: that needs camera calibration.
- Unknown or low-confidence cases go to "manual review" and are never forced into a label.

### Stack
- Python 3.11, OpenCV (quality gate, preprocessing).
- A pretrained road-damage detector (YOLO family, trained on RDD2022 or a pothole set). Use it only after checking that the weights are available, the classes fit, and the licence allows it.
- FastAPI backend (`POST /api/analyze`), simple web UI (upload → result → report), one public HTTPS service.
- No microservices. One deployable service, built from this repo.

## 3. Data and licences (verify every item before use)

| Source | Use | Licence: to check |
|---|---|---|
| RDD2022 (Road Damage Dataset 2022) | training / reference classes (D00 longitudinal crack, D10 transverse crack, D20 alligator crack, D40 pothole) | check the dataset page |
| Roboflow Universe pothole datasets | extra pothole data | each dataset has its own licence |
| Ultralytics YOLO | detector framework | **AGPL-3.0**: fine for a public repo, but the commercial plan needs an Enterprise licence (budget item) |
| Our own photos (Tashkent streets) | **test set** + local examples | own work; no faces or plates of people who did not consent (blur them or crop them out) |

Every source goes into the README with its licence. That is a deliverable.

## 4. Test set and metrics

- 30–100 carefully labelled images beat 100 random unlabelled ones.
- Split by scene or video, never neighbouring frames of the same clip into train and test.
- Record: model version, input size, confidence threshold, hardware.
- Report: precision, recall (mAP only if the labels and the computation are correct), quality-gate reject rate, latency (upload vs pure inference, after warm-up), cost per image.
- Show night or rain results separately **only if such images are really in the test set**.
- Keep a list of failure cases (shadows, puddles, manhole covers, wet asphalt) for the "known failures" slide.

## 5. Engineering risks

| Risk | Mitigation / honest limit |
|---|---|
| Night / rain | separate metrics per group; no robustness claims without tests |
| Unknown defect types | low confidence → manual review |
| False positives | confidence threshold, error log, test on separate scenes |
| Pothole depth / area | not claimed without calibration |
| Slow inference | measure on the real deploy hardware; state input size and warm-up |
| Local roads | pilot on one route with permitted local data collection |

## 6. Pilot economics (assumptions to replace with real numbers)

| Item | Example assumption |
|---|---|
| Pilot price for one organisation | $500 / month |
| Infrastructure and storage | $50–150 / month |
| Support and manual review | $100–200 / month |
| Margin before other costs | ~$150–350 / month under these assumptions |

ROI = (savings − pilot cost) / pilot cost × 100%. For example, $800/month of confirmed savings at a $500/month price gives 60%. **This is an example, not a result.**
Cost per image = (real infra + compute + storage) / real number of processed images. Include manual review, support and data collection, not only the cloud bill.

## 7. Plan (T = actual start; hard deadline Sun 11 Oct 13:00 Tashkent)

| From start | Work → required result |
|---|---|
| T+0:00–0:45 | pick scenario, check licences, agree architecture + fallback |
| T+0:45–2:00 | run inference on 5–10 images → **go RoadProof / switch to LensCheck** |
| T+2–5 | CV pipeline: upload, preprocessing, detection, confidence, boxes |
| T+5–7 | quality gate + decision engine; clear messages for bad inputs |
| T+7–9 | web UI + report |
| T+9–10 | end-to-end local test |
| T+10–12 | label test set, compute errors |
| T+12–13 | measure latency, estimate cost per image |
| T+13–15 | public HTTPS deploy; open from a laptop and a phone |
| T+15–16 | test unknown inputs, huge or wrong files, network errors |
| T+16–17 | README, data sources, licences, run instructions |
| T+17–19 | slides with screenshots and **real** metrics |
| T+19–20 | record backup demo, prepare a local copy |
| T+20–21 | rehearsal: 7 min + 3 min Q&A |
| T+21–22 | critical fixes only |
| T+22–23 | final smoke test, freeze, check that the deployed commit matches the submission |

## 8. Roles (three areas; map to people and agents in `docs/team.md`)

- **A. Computer vision:** model, preprocessing, inference, quality gate, tests, error analysis, latency → a CV module that can be tested.
- **B. App and deploy:** API, UI, integration, HTTPS, phone test, error handling → a working product.
- **C. Data, economics, pitch:** test-set labelling, metrics, sources and licences, costs, README, slides, rehearsal.

One person owns final integration. Nobody edits the same files in parallel without agreeing first.

## 9. Deck (7 min hard stop)

1. RoadProof / Startup: name, team, one-liner (20 s)
2. Problem and user: who inspects roads, what takes time, who pays; facts kept apart from hypotheses (40 s)
3. **Live demo**: the jury's image → result → quality gate → report (2 min)
4. Architecture: image → quality gate → model → decision engine → report (50 s)
5. Technical evidence: test size, metrics, latency, cost, failure cases (1 min 10 s)
6. Budget and ROI: payer, pilot price, costs, assumptions, what the pilot will measure (1 min 30 s)
7. Next steps: one-route pilot, permitted local data, quality check, scale decision (30 s)

One person presents, one runs the demo, one handles technical questions. No hand-over during the demo.

## 10. Jury Q&A (short answers)

1. **Why road damage?** The visual result turns into a concrete process: find and prioritise sites for inspection. It does not replace the engineer.
2. **How is this more than a pothole detector?** Detection is one stage. We add an input quality gate, uncertainty handling, transparent priority rules and a structured report, all checked on our test set.
3. **What is yours if the model is pretrained?** The pipeline, error handling, quality gate, evaluation and process integration. Sources and licences are listed.
4. **How did you measure accuracy?** On a separate test set of N images labelled by written rules: [real metrics]. This is a preliminary check, not proof of production readiness.
5. **Night and rain?** We don't claim equal quality. We show the groups we tested; where data is missing we say so and ask for a retake or manual review.
6. **Where does inference run, and how fast?** On [real server]; measured on N images, with upload time and pure inference reported separately.
7. **Cost per image?** (infra + compute + storage) / real number of requests = [real figure]: a prototype estimate, not a production tariff.
8. **Who pays?** An organisation that inspects roads regularly. A one-route pilot compares manual inspection time with and without RoadProof.
9. **How did you use LLMs?** To speed up development. Generated code was reviewed and tested, and the team can explain every component.
10. **What stops a rebuild in a weekend?** Not the detector. The edge is a validated local dataset, an error history, adaptation to local capture conditions and process integration, all of which the pilot has to confirm.

## 11. Pre-submission checklist

- [ ] HTTPS link opens on another device (laptop + phone)
- [ ] The jury can upload their own photo
- [ ] Wrong format, huge file and unsuitable image are handled gracefully
- [ ] Metrics are computed on the test set, not on training images
- [ ] Latency is measured on the real hardware, with the conditions written down
- [ ] Cost per image is explained with a formula and assumptions
- [ ] README: install, run, architecture, data sources, licences
- [ ] No keys, confidential data, faces or real plates without consent in the repo
- [ ] Slides contain only verified results
- [ ] Backup demo recording + local copy
- [ ] Repo made **public**; the submitted commit is fixed and deployed before 13:00

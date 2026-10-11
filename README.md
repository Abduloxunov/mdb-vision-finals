# CarDoctor — MDB Vision

**See the damage. Know what to do. Find who can fix it.**

CarDoctor turns photos of a car, and the owner's own words, into one report. The report lists every visible damage, says how urgent the problem is with a source for each piece of guidance, and names who to contact.

## The idea

Our starting idea was a trained vision model working together with an LLM. The model sees **physical damage** (dents, scratches, cracks, broken glass and lamps, flat tyres). The owner's words cover **problems a photo cannot show**, such as overheating, an oil-pressure light or a brake warning. Both lead to sourced guidance and a next step.

One photo is not enough to judge a car. **CarDoctor checks many photos of the same car** (front, rear, left, right…), finds the damage on each one and merges everything into a single report with a car map of the damaged sides.

## Two applications

| | 🚗 Sell / Buy a car | 🚚 Fleet & trucks |
|---|---|---|
| Who uploads | The seller, when listing the car on a marketplace | The driver, when something goes wrong on the road |
| Input | Photos from every side, plus optional notes | Photos and/or the problem in their own words ("overheating, steam"), plus engine and parking-brake answers |
| What CarDoctor does | Finds every visible damage on every photo and marks the damaged sides on the car map | Detects damage, matches the described symptom to sourced records and asks the missing safety questions |
| Output | A **condition report the buyer sees** before visiting | An **urgency verdict** (stop / inspect soon / routine) and **which technician to call** |
| Who pays (plan) | Marketplace per report or per listing | Fleet per vehicle per month; workshops per referred job |

## How it works

```
photos (many, each tagged with a side) ─► RF-DETR damage detector (fine-tuned) ─┐
owner's words + car model + yes/no context ──────────────────────────────────────┼─► retrieval from 28 sourced records
                                                                                  │   (BM25 + E5/Qdrant, scope checks)
                                                                                  ▼
                       verdict (worst sourced urgency) · car map · damage list · workshop contacts
                       · optional LLM explanation that may only cite retrieved records · downloadable report
```

- **Vision:** RF-DETR Nano fine-tuned by us on CarDD (6 classes). Runs on every photo, on CPU.
- **Knowledge:** 28 Markdown records with 20 sources (NHTSA, manufacturer manuals for Cobalt, Lacetti, Nexia and Damas, 3M, I-CAR and others). Records tied to a specific car model are shown with a "check that your model year is covered by this manual" note.
- **LLM (optional):** Gemini 2.5 Flash Lite through OpenRouter explains only the retrieved records, citing a source for each claim. Photos are never sent to it.
- **Workshops:** published contacts from `kb/workshops.md`, matched by car brand and repair type. They are contacts, not verified referrals or quotes.
- **Nearest technician (demo):** `kb/demo-technicians.json` holds 8 **fictional** technicians with approximate Tashkent district coordinates, clearly labelled as demo data in the app. With **📍 Use my location**, the browser sorts them by distance and each one links to a Google Maps route. Location stays in the browser and is never sent to our server. A real deployment would replace this file with verified partner workshops.

## Run the app now

From this checkout in PowerShell:

```powershell
Set-Location D:\hakathon_wiut\finals\mdb-vision-finals
.\start-app.ps1
```

Open **http://127.0.0.1:8766/**. Choose **Sell / Buy** or **Fleet & trucks**, add photos (several sides) and/or describe the problem, then press the button.

**Public https demo** (laptop stays on): in a second window run
`cloudflared tunnel --url http://127.0.0.1:8766 --http-host-header localhost:8766` and share the printed `https://….trycloudflare.com` link. The server stays bound to 127.0.0.1; the tunnel forwards to it. The older visual-reference experiment uses port 8765; the new integrated app uses 8766.

The existing Python environment is `D:\hakathon_wiut\.venv`. The trained checkpoint and E5/Qdrant index are already present locally. No download is required to run this setup. First analysis loads the two models; later analyses are faster.

Optional checkpoint override:

```powershell
.\start-app.ps1 --checkpoint D:\path\checkpoint_best_ema.pth
```

Use only trusted training checkpoints. A matching `CHECKPOINTS.json`, when present, is verified before loading. Uploads accept images only.

## AI configuration

The existing ignored `.env` supplies `OPENROUTER_API_KEY`; `.env.example` is the shareable template. Gemini 2.5 Flash Lite is accessed through OpenRouter. Select “Add an AI explanation” to make one bounded request from the backend. The browser never receives the key. Only text evidence/context goes to the LLM, not the photo. Leave the option unchecked for offline evidence. A missing key, invalid answer or provider failure retains the retrieved source guidance.

## Implemented stack

| Stage | Current implementation |
|---|---|
| CV | RF-DETR Nano 1.11.2; fine-tuned on CarDD; 384-pixel model input |
| Classes | Dent, scratch, crack, glass shatter, lamp broken, tire flat |
| Applicability | Explicit component, model, propulsion, manual and boolean context checks |
| Retrieval | Pinned multilingual E5-small + local Qdrant; BM25/vector rank fusion; explicit keyword fallback |
| Evidence | 28 Markdown records, 20 sources; source locators and conditions preserved |
| Explanation | Gemini 2.5 Flash Lite through OpenRouter; bounded JSON, record/source binding checks |
| UI / server | Responsive HTML/CSS/JavaScript (two modes, multi-photo, car map, verdict, workshop cards, print/PDF); Python loopback HTTP service with `/api/assess` (whole car) and `/api/analyze` (single photo) |
| Report | Markdown downloaded by the browser |

A damage label does not identify its component, hidden cause, severity or repair price. The user confirms the component. The background class is excluded. Scores are uncalibrated. Generated explanations remain unreviewed; valid citation IDs alone do not prove factual support.

## Measured results

The current app uses the best EMA checkpoint selected at epoch 10 from a completed 12-epoch CarDD run: **2,816 training** and **810 validation** images on NVIDIA L4. Its selected-checkpoint validation mAP@50 is **0.7397** and mAP@50-95 **0.5931**. The ten-epoch continuation training call took **1505.7 seconds**, after the original two-epoch pilot took 313.9 seconds.

Both checkpoints were then tested locally on the same **374 official test images / 785 targets**, excluded from cloud training. Test mAP@50 improved **0.6630 to 0.7354**, mAP@50-95 **0.5342 to 0.5916**, and macro F1 **0.6306 to 0.7135** at confidence 0.35 / IoU 0.50. Cracks remain weak and small-object AP declined. These are damage-box metrics, not mechanical diagnosis accuracy. [Complete comparison and per-class results](docs/CARDOCTOR-MODEL-COMPARISON.md).

The current app passes twelve pipeline tests and nine real browser workflow checks with the improved checkpoint. Earlier pilot measurements on a repeated single validation image with warm CPU models and no LLM took 0.351–0.410 seconds within the server, median 0.364 seconds. A cold browser analysis including one LLM response took 22.257 seconds. This is a small local engineering check, not a throughput or production benchmark. The whole-car flow (`src/assess.py`) adds five tests (17 in `src/` in total). Its UI was checked in a headless browser on desktop and phone sizes with a stand-in detector; run it once with the real checkpoint before the demo.

See [training results](docs/CARDOCTOR-HF-RESULTS.md), [app setup and API](docs/CARDOCTOR-APP-SETUP.md), and [submission readiness](docs/CARDOCTOR-SUBMISSION-READINESS.md).

## Reproduce setup on another Windows machine

The exact local package snapshot is in `requirements-app-local.txt` (Python 3.12.10). The existing repo rule targets Python 3.11; this local build has not been verified under 3.11. Use a D: virtual environment and D: caches; avoid reinstalling packages into the current working environment during the deadline.

Copy the trusted weights separately, point `--checkpoint` at them, and set the backend-only API key locally. Build the pinned text model/index with `kb/setup_vector.py` then `kb/vector_store.py ingest` following [the vector guide](kb/VECTOR-RAG.md). Query-time model downloads are disabled. This app currently runs on the prepared Windows D: environment; Linux/public hosting requires an adapter and deployment verification.

## Tests

```powershell
D:\hakathon_wiut\.venv\Scripts\python.exe -B -m unittest discover -s src -p 'test_*.py'
D:\hakathon_wiut\.venv\Scripts\python.exe -B -m unittest discover -s kb -p 'test_*.py'
```

`src/browser_check.cjs` uses preinstalled Chrome and Playwright with a private D: profile. Its current real-photo test uses a private validation image; do not publish that screenshot as consent-cleared demo media. Run with the bundled Node module path described in the app setup guide.

## Sources, licences and AI use

- [RF-DETR](https://github.com/roboflow/rf-detr): official Nano/core model implementation; review the exact variant's Apache-2.0 terms. CarDoctor training changes its weights, not the dataset rights.
- [CarDD](https://github.com/CarDD-USTC/CarDD): research damage data, not repair-cost or mechanical-diagnosis labels. User authorized research use; author consent/access terms are unverified. Keep data and checkpoints private pending a rights review before redistribution or commercial use.
- [Multilingual E5-small](https://huggingface.co/intfloat/multilingual-e5-small/tree/614241f622f53c4eeff9890bdc4f31cfecc418b3): pinned MIT-published model; [Qdrant client](https://github.com/qdrant/qdrant-client): Apache-2.0. Model scores are not our accuracy measurements.
- [Source register](kb/sources.md): manufacturer and repair guidance summarized with attribution and applicability. Full manuals/articles are not redistributed. Mechanic review is pending.
- Coding assistants helped research, implementation, training orchestration, testing and documentation. The runtime LLM explains retrieved text; it is not the detector. Graph RAG, VLM observations, visual-reference retrieval, confirmed prices and workshop maps are not implemented in this integrated MVP.

## Team and delivery

Davlatyor Abduloxunov: lead / final submission; Muhammadjon Xalimov: data and measurements; Bexruz Xasanov: KB, CV experiments and integrated app built here at the user's latest instruction. Presentation/demo planning continues with teammates. This local handoff does not merge another developer's branch. Development handoff is available for review in [PR #6](https://github.com/Abduloxunov/mdb-vision-finals/pull/6). Public deployment and final submission have not been performed by this chat.

Code freeze: **11 October 2026, 13:00 Asia/Tashkent**. The lead still needs the public HTTPS demo, public repository, permitted demo media, exported deck and final form submission. [Assignments](docs/tasks.md) and [official checklist](docs/submission.md) retain the team ownership/history.

## Follow-on training status

The CarDD continuation completed and its tested checkpoint is configured in the app. [Continuation controls and code](experiments/cardoctor-hf/CONTINUATION.md).

At the user's subsequent instruction, a separate two-epoch **VehiDE native seven-class pilot** was launched on Hugging Face L4. The first attempt failed before its first epoch because of corrupt JPEGs. Strict full pixel decoding found 16 corrupt photos, which were excluded; the repaired package has 11,589 train and 2,322 validation images and was uploaded and verified for a bounded retry. Its seven labels remain separate from the tested six-class CarDD app. The repaired retry has **COMPLETED**: [Hugging Face job](https://huggingface.co/jobs/abduloxunov/6acb26e6095c57808931b22c). Reconciled completed-job durations plus its 40-minute cap give a conservative hardware estimate/cap of $1.106639 within the authorized $2 budget. Trainer-reported final EMA validation mAP50 is 0.3843 and mAP50-95 is 0.2437. Full local evaluation on 2,322 validation photos measured mAP50 **0.3714**, mAP50-95 **0.2347**, macro F1 **0.3878** and micro recall **0.2464** at confidence 0.35 / IoU 0.50. These are model-selection validation results, not an independent test or a direct comparison with CarDD. The app retains CarDD. [Trial results and evaluation protocol](docs/CARDOCTOR-VEHIDE-RESULTS.md). This estimate does not establish account billing/remaining credit or storage charges.


Kaggle follow-up: [audited datasets and private Hugging Face preparation](docs/CARDOCTOR-KAGGLE-HF-PREPARATION.md). VehiDE is a separate native seven-class experiment; it does not change the current CarDD app or its metrics.

Current implementation: [photo and text symptom pipeline](docs/CARDOCTOR-PIPELINE.md), with supported-component gating, 12 pipeline checks and 9 browser checks.

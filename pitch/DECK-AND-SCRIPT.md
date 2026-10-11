# CarDoctor: defence deck and 7-minute script

Mode on slide 1: **Startup**. Total speaking time ≈ 6:40, leaving 20 s of buffer. The timing follows the jury's recommended split: problem 1, demo 2, technology 2, budget 1.5, next 0.5.
Every number below comes from our measurements or a cited source. Items marked **[FILL]** must be completed from a real source before showing; leave them out if you cannot.

---

## Slide 1: Title (0:00–0:15)
**On slide:** CarDoctor · "See the damage. Know what to do. Find who can fix it." · **Mode: Startup** · Team MDB Vision: 3 photos with names and roles · demo link + QR code
**Say:** "We are MDB Vision. CarDoctor is a startup that turns photos of a car and the owner's own words into a decision: what is damaged, how urgent it is, and who can fix it."

## Slide 2: Problem and user (0:15–1:15)
**On slide (3 facts, sources in small text):**
- 9,364 road crashes in Uzbekistan in 2024, each needing a damage check (Kun.uz, Feb 2025)
- ~240,000 used cars sold in H1 2026; parliament is fining odometer fraud (Kun.uz, 2026)
- 2 of 3 drivers don't trust repair shops (AAA survey)

**Two users:** 🚗 buyers and sellers on used-car marketplaces · 🚚 truck and taxi fleets
**Say:** "Buying a used car, you can't see what's hidden, and the seller won't tell you. A fleet manager whose truck breaks down on the road doesn't know whether to stop it or keep driving, or who to call. Today both rely on guesswork and phone calls."

## Slide 3: Live demo (1:15–3:15) **← the most important slide**
**On slide:** only the demo link + QR code, so the jury can open it on their phones.
**Do (2 minutes, practised):**
1. Sell mode → **Sample car 1** (4 photos, Front/Rear/Left/Right) → *Check the car* → verdict card, **3D car** with red areas, damage boxes on each photo, sourced guidance, download report. (~60 s)
2. Fleet mode → no photo → "Chevrolet Cobalt", "engine overheating, steam" → 🔴 *Stop and get help* with the manual source → **📍 Use my location** → nearest technician + Route. (~45 s)
3. "Please try it on your phone with your own photo." (~15 s)

**Backup:** if the network fails, play the recorded video (`pitch/demo.mp4`) immediately. The clock doesn't stop.

## Slide 4: How it works, the pipeline (3:15–4:15)
**On slide (diagram):**
```
 Photos (many, tagged by side) ─► [1] RF-DETR Nano damage detector (our fine-tune) ─► damage boxes + labels
 Owner's words + car model     ─► [2] Retrieval: BM25 + E5 embeddings (Qdrant) + scope checks ─► 28 sourced records
                                                         │ (model, propulsion, manual, engine/brake context)
                                                         ▼
                               [3] Decision: worst sourced urgency → verdict (stop / inspect / routine)
                               [4] LLM (Gemini 2.5 Flash Lite) explains ONLY retrieved records, each claim cites a source
                               [5] Output: 3D damage map · report · nearest technician + route
```
**Say:** "This is a system, not one prompt. Vision finds the damage; retrieval finds sourced guidance for that car and that symptom; the decision comes from the sources, not the LLM. The LLM only explains what was retrieved and must cite it. Photos never go to the LLM."

## Slide 5: Our model and measured quality (4:15–5:15)
**On slide (all measured by us):**
| | Result |
|---|---|
| Model | RF-DETR Nano, fine-tuned on CarDD (6 classes), NVIDIA L4, 12 epochs (Hugging Face Jobs) |
| Data | 2,816 train / 810 validation images |
| **Test set: 374 images, 785 damages, never used in training** | **mAP50 0.735 · mAP50-95 0.592 · macro F1 0.714** |
| Improvement over our 2-epoch pilot | mAP50 0.663 → 0.735 |
| Speed | 0.36 s per photo on a laptop CPU (median, warm), no GPU needed |
| Knowledge base | 28 records, 20 sources (NHTSA, Cobalt/Lacetti/Nexia/Damas manuals, 3M, I-CAR) |

**Known failure cases (say them):** cracks and small defects are weak; it hasn't been tested at night, in rain or on local cars yet; a photo can't show hidden damage.
**Say:** "We trained and tested it ourselves. Weak points: cracks and small defects. That is why the report says 'inspect', never 'guaranteed'."

## Slide 6: Why it's hard to copy (5:15–5:45)
**On slide:**
- Own fine-tuned detector + evaluation pipeline (training, test split, per-class results)
- Local knowledge: model-specific records for Cobalt, Lacetti, Nexia, Damas with manual page references
- Safety logic: the system asks "engine running? parking brake released?" before it gives model-specific advice
- Next data moat: our own photos of Uzbek cars + confirmed repair outcomes from partner workshops

**Say:** "Another team with the same LLM gets a chatbot. They don't get our trained detector, our sourced local records, or the safety checks."

## Slide 7: Business, budget and ROI (5:45–6:30)
**On slide:**
- **Who pays:** marketplaces per condition report · fleets per vehicle per month · workshops per referred job
- **Cost per inspection** = CPU time (≈0.36 s × photos) + optional LLM call. **[FILL]** price per CPU hour (Hugging Face pricing page) and per-token LLM price (OpenRouter page), then compute it.
- **Pilot (3 months):** 1 marketplace or 1 fleet in Tashkent, team of 3, CPU server, our photo collection. **[FILL]** salaries/server/data costs and the payback assumption, each stated.
**Say:** "Costs are pennies per check because it runs on CPU. Revenue comes from three sides of the same report." *(Only say numbers you filled from a source.)*

## Slide 8: Next steps (6:30–6:40)
**On slide:** local test set (night, rain, Uzbek cars) · part-level 3D marking (part segmentation) · verified partner workshops with prices · Uzbek/Russian UI
**Say:** "Next: test on local cars at night and in rain, mark the exact part in 3D, and sign the first partner workshops. Thank you."

---

## Q&A prep (3 minutes; any member may be asked)
- **"Is it just GPT?"** No. The detector is our RF-DETR fine-tune; the LLM is optional and only explains retrieved records.
- **"Accuracy?"** Test mAP50 0.735 on 374 held-out CarDD images. Not yet measured on Uzbek cars.
- **"Data licence?"** CarDD is research data; weights stay private pending a rights review. Demo photos are our own.
- **"The technicians on the map?"** Labelled demo data; the real contacts and the Google Maps search are real.
- **"Hidden damage?"** We don't claim it. The verdict says inspect, and the mechanic decides.

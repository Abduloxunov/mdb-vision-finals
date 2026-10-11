---
title: Uzbek document AI — OCR that works on real documents (Latin + Cyrillic)
track: cv
status: inbox
added_by: Abduloxunov
date: 2026-09-18
tags: [ocr, document-ai, vlm, low-resource-language, synthetic-data, local-market]
---

# Uzbek document AI (OCR)

## One-liner
Photograph any Uzbek document — a handwritten form, an old Cyrillic book page, a crumpled
receipt, a prescription — and get back correct, editable text with the layout preserved, in
whichever script you want, Latin or Cyrillic.

## Problem
- Uzbekistan runs on **two alphabets at once**: the country moved to Latin (completed 2023),
  but Cyrillic is still everywhere — archives, signage, older people's handwriting, older
  state documents.
- Existing OCR handles clean printed text and fails on what people actually photograph:
  phone photos at an angle, handwriting, mixed scripts, real layouts.
- Result: banks, clinics, universities and government offices still re-type documents by hand.

## Solution
```
photo → deskew / dewarp → text detection → text recognition → language correction → output
```
1. **Detection** — use an existing scene-text detector (DBNet / CRAFT / PaddleOCR detector).
   Do not build this ourselves.
2. **Recognition** — the part where we add value. Fine-tune a small VLM (Qwen3-VL class) or a
   TrOCR-style model on Uzbek text with LoRA / QLoRA; fits on one consumer GPU.
3. **Synthetic data trick** — render Uzbek text (Uzbek Wikipedia, news sites) in many fonts,
   then add blur, skew, shadows, JPEG artefacts, paper texture. Tens of thousands of labelled
   samples in hours, then fine-tune on a few hundred real photos we take ourselves.
4. **Language correction** — dictionary / small LM constrained to Uzbek fixes character-level
   errors. Uzbek is agglutinative, so morphology helps here (see UzMorphAnalyser,
   arXiv:2405.14179).
5. **Output** — editable text, export to Word/PDF, plus a correct **Latin ⇄ Cyrillic converter**
   (ў/oʻ, қ/q, ғ/gʻ, ҳ/h, х/x — naive converters get these wrong).

### Scope levels — pick deliberately
| Level | Reads | Difficulty | Note |
|---|---|---|---|
| A. Printed text | books, newspapers, printed forms | easiest | partly solved already |
| B. Structured documents | ID cards, invoices, receipts, prescriptions, certificates | medium | **highest business value** |
| C. Handwriting | forms, student work, archives | hardest | **most original** |

Recommended: **B as the core demo, C as the wow moment.**

## Why now / what's new
- Fine-tuning a VLM on a single consumer GPU is now routine (LoRA/QLoRA, Unsloth).
- Small 3B–4B VLMs run locally, so the whole thing can work offline — important for
  government and medical settings.
- Recent benchmark work shows OCR still struggles beyond a handful of well-resourced scripts
  (GlotOCR Bench, arXiv:2604.12978). The gap is documented, not assumed.
- See [[research-cv-landscape-sep-2026]].

## Existing alternatives
- **Tesseract** ships Uzbek models for both scripts: `uzb` (Latin) and `uzb_cyrl` (Cyrillic).
  **So "the first Uzbek OCR" is a false claim — judges may know this.** They are old, trained
  mostly on clean print, and break on phone photos, handwriting and mixed scripts.
- **Google Vision / Azure Document AI** — handle Cyrillic and Latin generically, but model no
  Uzbek language specifics, so they output plausible-looking wrong words. Nobody is optimising
  for this market.
- **Our positioning:** not "the first", but **"Uzbek OCR that actually works on the documents
  people really have."** `(to verify: run both on our test set before the finals)`

## Demo plan (what works on stage in 2 days)
- Hand the judges a stack of real documents (handwritten form, old Cyrillic page, crumpled
  receipt, prescription). **They pick one**, we photograph it live, text appears in seconds.
- **Side-by-side with Google Vision / Tesseract failing on the same photo — this comparison
  IS the demo.**
- Toggle output script Latin ⇄ Cyrillic live.
- Airplane-mode moment: it still works offline.

## Data & tech
- Data: synthetic rendered corpus + a few hundred real photos we collect; a held-out test set
  we build and describe honestly.
- Models: text detector (pretrained) + fine-tuned small VLM / TrOCR; Uzbek dictionary or small LM.
- Stack: Python, PyTorch, PEFT/LoRA, OpenCV; simple web or phone front-end.
- Biggest technical risk: **handwriting data**. Synthetic handwriting is far harder to fake than
  print. Mitigation: start collecting real filled forms from friends/classmates early.
- Second risk: this reads as much like NLP as vision — keep the visual pipeline visible in the pitch.

## Business
- **KYC / onboarding** for banks and telecoms (ID and document capture).
- **Archive digitisation** for government bodies, courts, libraries — Cyrillic-era material.
- **Insurance claims**, **education paperwork**, **clinics** (prescriptions, referrals).
- Buyers here already pay for foreign OCR that performs worse on their own documents.
- Model: per-page or per-document API pricing, plus an on-prem licence for state bodies that
  cannot send documents abroad.

## Score (1–5 each) — provisional
| Criterion | Weight | Score | Why |
|---|---|---|---|
| Innovation & Originality | 25% | 5 | Low-resource, dual-script, genuinely underserved |
| Technical Complexity | 25% | 5 | VLM fine-tuning, synthetic data, correction pipeline |
| Impact & Practicality | 25% | 5 | Everyone here handles these documents |
| Presentation / demo-ability | 15% | 4 | Great when it works; failures are visible |
| Business Potential | 10% | 4 | Clear buyers already paying for worse tools |
| **Weighted total** | | **4.75** | |

## Open questions
- Which document type do we make the core demo — ID cards, receipts or handwritten forms?
- Do fonts for Uzbek Latin with the correct oʻ / gʻ glyphs exist in enough variety for synthetic data?
- Can we get permission to photograph real documents (privacy — anonymise or use our own)?
- How do we measure accuracy fairly (CER/WER on our own test set) and present it honestly?

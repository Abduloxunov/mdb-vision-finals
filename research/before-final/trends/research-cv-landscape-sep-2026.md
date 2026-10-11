---
title: CV landscape, September 2026 — models, trends, local context
type: news
track: cv
released: 2026-09
added_by: Abduloxunov
date: 2026-09-18
tags: [landscape, models, detection, segmentation, vlm, edge, uzbekistan]
---

# CV landscape, September 2026

Baseline research for the Computer Vision track. Collected from web sources on 2026-09-18 —
**summaries, not hands-on tests**. Verify any benchmark number on the model's own page before
relying on it in a pitch. `(unverified)` marks claims we have not checked ourselves.

## Summary (3 lines)
In 2026 you rarely train from scratch: you prompt or lightly fine-tune a foundation model and
spend your effort on the pipeline, the product and the demo. Detection is led by RF-DETR and
YOLO26, segmentation/tracking by SAM 3 / 3.1, and small open VLMs now fine-tune on one consumer
GPU. Edge / on-device inference is becoming the default for real-time vision.

## Models worth building on

### Detection
| Model | Why it matters | Watch out |
|---|---|---|
| **RF-DETR** | Apache 2.0; first real-time model past **60 mAP on COCO**; leader on **RF100-VL** (domain-transfer benchmark → predicts how well it handles *our* custom data). DINOv2 backbone, anchor-free, NMS-free. | Bigger than YOLO for edge |
| **YOLO26** (Ultralytics) | NMS-free end-to-end, MuSGD optimizer, **up to 43% faster CPU inference** `(unverified)` → best for laptop/phone demos | Ultralytics licensing is AGPL — check if commercial use is judged |
| **YOLOv12** | Solid, well-documented fallback | Superseded |

### Segmentation & tracking
- **SAM 3** (Meta, released 2025-11-19) — *promptable concept segmentation*: give it a **text
  prompt or image example** and it detects, segments and **tracks every instance** of that
  concept across a video. Open weights; SA-Co benchmark released with it. arXiv:2511.16719
- **SAM 3.1** (2026-03-27) — adds **Object Multiplex** (shared-memory multi-object tracking),
  reported ~**7× speedup at 128 objects** on a single H100. `(unverified)`

### Zero-shot detection (no training needed)
- **Grounding DINO**, **YOLO-World** — detect from a text prompt at inference time
  ("person wearing a hard hat"). Ideal for a hackathon: a working demo without labelling.

### Open VLMs (image + text reasoning)
- Qwen3-VL / Qwen3.5, InternVL3.5, GLM-4.5V / 4.6V, Molmo2, MiniCPM-V, Kimi-VL, Florence-2,
  Pixtral (Apache 2.0).
- **Small 3B–4B models run on modest hardware**; LoRA/QLoRA fine-tuning of a VLM fits on a
  single consumer GPU (RTX 3060/4070 class). Unsloth reports small-model LoRA from ~5 GB
  VRAM. `(unverified)`

## Trends
- **Edge / on-device is becoming the default** for real-time vision: lower latency, lower
  cost, better privacy. A demo running live on a laptop or phone beats a cloud API call on stage.
- **"Physical AI"** (vision + sensors + real-world action) was the dominant CES 2026 theme.
- Startup opportunity is **narrow and deployable**: quality inspection, warehouse/retail vision,
  farm monitoring, fleet and device monitoring.

## Uzbekistan context
Government-stated CV priorities:
- **Agriculture** — crop yield forecasting, phytosanitary risk alerts, pasture monitoring.
- **Transport** — road surface and railway infrastructure monitoring, driver hazard alerts, ITS.
- **Construction & industry** — violation detection, production monitoring via video analytics.

Ecosystem:
- **TASS Vision** (retail analytics) and **United Soft** at IT Park → retail vision is partly taken.
- **AI Leaders 2026** executive programme with Stanford HAI + OpenAI Academy launched 2026-04-08.
- **ICT Week Uzbekistan: 22–25 Sep 2026, Tashkent** — overlaps our elimination window.

### The clearest gap: Uzbek-script document AI
Uzbek OCR/handwriting data is scarce; the country uses **both Latin and Cyrillic** after the
2023 transition; recent benchmarks show OCR still struggles outside a handful of scripts.
Note: Tesseract *does* ship `uzb` and `uzb_cyrl` models — the gap is quality on real photos,
handwriting and mixed scripts, not absence. → [[uzbek-document-ocr]]

## Suggested prep stack
`supervision` + `roboflow` (pipeline) · **RF-DETR** or **YOLO26** (detection) · **SAM 3**
(segmentation/tracking) · **Grounding DINO / YOLO-World** (zero-shot) · **Qwen3-VL** class
(reasoning over images) · **Unsloth + QLoRA** (fine-tuning) · Colab / Kaggle (GPUs).

## Related
[[uzbek-document-ocr]] · [[sign-language-translator]]

## Sources
- https://blog.roboflow.com/best-object-detection-models/
- https://www.ultralytics.com/blog/best-object-detection-models
- https://docs.ultralytics.com/models/sam-3
- https://ai.meta.com/blog/segment-anything-model-3/
- https://arxiv.org/abs/2511.16719 (SAM 3)
- https://blog.overshoot.ai/blog/vlm-survey-2026
- https://www.bentoml.com/blog/multimodal-ai-a-guide-to-open-source-vision-language-models
- https://www.spheron.network/blog/gpu-vram-requirements-fine-tune-llm-2026/
- https://jetruby.com/blog/ces-2026-highlights-ai-computer-vision-iot-startups/
- https://yuz.uz/en/news/suniy-intellekt-va-raqamlashtirish-sohasidagi-vazifalar-korib-chiqildi
- https://timesca.com/uzbekistan-ai-economy/
- https://anewz.tv/region/central-asia/24352/ict-week-uzbekistan-2026-focuses-on-startups-and-ai/news
- https://arxiv.org/pdf/2407.05006 (Turkic Central Asian language processing)
- https://arxiv.org/pdf/2604.12978 (GlotOCR Bench)
- https://arxiv.org/abs/2209.08538 (RDD2022 road damage dataset)
- https://github.com/tesseract-ocr/tesseract/wiki/Data-Files/87023a8643202525431653da95e0f7d91616b7d9

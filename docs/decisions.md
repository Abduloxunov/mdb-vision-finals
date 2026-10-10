# Decisions and shared interfaces

Anything two parts of the code depend on (formats, function signatures, file paths, data links) goes here.

| Date/time | Decision | By |
|---|---|---|
| Sat 10 Oct | **Proposed** (needs lead OK): product = RoadProof (Startup), fallback = LensCheck if no detector works by T+2h. Details in `docs/strategy.md` | claude-2 (Muhammadjon) |
| Sat 10 Oct | **Proposed**: API contract `POST /api/analyze` (below). CV module and web app both code against it | claude-2 (Muhammadjon) |

## Proposed API contract — `POST /api/analyze`

Request: `multipart/form-data`, field `image` (JPG/PNG, max 10 MB).

Response `200` (JSON):
```json
{
  "request_id": "uuid",
  "quality": {
    "ok": true,
    "checks": {"min_side_px": 1080, "blur_var_laplacian": 182.4, "mean_brightness": 117.0},
    "reasons": []
  },
  "detections": [
    {"cls": "pothole", "conf": 0.81, "bbox_xyxy": [412, 530, 690, 701], "area_frac": 0.031}
  ],
  "priority": {"level": "high", "score": 0.74, "reasons": ["pothole conf 0.81 covers 3.1% of frame"]},
  "action": "Send inspector to verify within 48 h",
  "limitations": ["Confidence is not a measured severity", "Depth/area not measured (no calibration)"],
  "timing_ms": {"quality": 4.1, "inference": 0.0, "total": 0.0},
  "model": {"name": "<weights file>", "version": "<git sha or tag>", "imgsz": 640, "conf_thr": 0.25}
}
```
- If `quality.ok` is false, `detections` is `[]`, `priority.level` is `"retake"` and `reasons` say what to fix.
- Classes follow RDD2022 naming, mapped to readable names: D00 `longitudinal_crack`, D10 `transverse_crack`, D20 `alligator_crack`, D40 `pothole`.
- Errors: `400` (bad file), `413` (too large), `500`, all as `{"error": "<message>"}`.
- Every request is appended to a JSONL log (no image bytes, no personal data) for metrics, latency and cost.

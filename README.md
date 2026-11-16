# OpenCV Real-time Quality Check (Python + Node + React)

A lightweight starter project showing **OpenCV best practices** for a real-time use case:

- Capture webcam frames in React
- Send frame to Node API
- Analyze frame quality in Python/OpenCV
- Return actionable guidance (`too_dark`, `too_blurry`, etc.)

## Real-time scenario

Before doing expensive tasks like OCR, face recognition, or barcode scanning, validate frame quality first.  
This helps avoid wasted compute and poor user experience.

## Why this is a best-practice pattern

1. **Early quality gate**: reject bad frames first.
2. **Simple, explainable metrics**:
   - Brightness (mean grayscale)
   - Blur score (Laplacian variance)
3. **Structured API response** for frontend/monitoring.
4. **Separation of concerns**:
   - React = camera + UI
   - Node = API orchestration
   - Python/OpenCV = image analytics

## Project structure

- `src/python/processor.py` — OpenCV analysis logic
- `src/node/server.js` — REST API (`/api/analyze`)
- `src/react/src/App.jsx` — webcam capture + UI result display

## Prerequisites

- Python 3.9+
- Node.js 18+
- pip package: `opencv-python`

## Setup

### 1) Python dependency

```bash
pip install opencv-python
```

### 2) Start Node API

```bash
cd src/node
npm install
npm start
```

API runs on `http://localhost:4000`.

### 3) Start React UI

```bash
cd src/react
npm install
npm run dev
```

Open the Vite URL (usually `http://localhost:5173`).

## API contract

### POST `/api/analyze`
Request:
```json
{
  "imageBase64": "data:image/jpeg;base64,..."
}
```

Response:
```json
{
  "ok": true,
  "status": "needs_attention",
  "metrics": {
    "brightness": 55.12,
    "blurScore": 62.44
  },
  "issues": ["too_dark", "too_blurry"],
  "guidance": {
    "too_dark": "Increase ambient light or move closer to a light source.",
    "too_bright": "Reduce direct glare/light intensity.",
    "too_blurry": "Hold camera steady or improve focus."
  }
}
```

## Guidance to resolve common issues

- **too_dark**: add light, increase camera exposure, avoid backlight.
- **too_bright**: reduce direct light, avoid reflections.
- **too_blurry**: stabilize device, improve focus distance, increase shutter speed if possible.

## Production notes (next steps)

- Tune thresholds using your own dataset/device.
- Add frame sampling strategy (e.g., every N frames).
- Add object/ROI-specific quality checks (face/document area only).
- Use queues/workers for high-throughput pipelines.
- Add observability: metric logs + alerting for quality drops.

## License

MIT (for demo use).
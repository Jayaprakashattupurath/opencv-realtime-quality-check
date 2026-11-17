# Application Test Cases (Python + Node + React)

This document lists practical test cases for the key features in the app.

---

## 1) React UI (Camera + Controls + Display)

### TC-UI-001: Page loads and core elements render
- **Feature**: App shell/UI rendering
- **Precondition**: React dev server is running
- **Steps**:
  1. Open the app URL in browser.
- **Expected**:
  - Title text appears: `OpenCV Real-time Image Quality Check`
  - Video element is visible
  - Button appears (`Pause Analysis` by default)

### TC-UI-002: Webcam permission granted
- **Feature**: Webcam initialization
- **Precondition**: Browser supports `getUserMedia`
- **Steps**:
  1. Load the page.
  2. Click **Allow** on camera permission prompt.
- **Expected**:
  - Live camera feed appears in video area.
  - No console error for media access.

### TC-UI-003: Webcam permission denied
- **Feature**: Error path for camera access
- **Precondition**: None
- **Steps**:
  1. Load page.
  2. Deny camera permission.
- **Expected**:
  - App should not crash.
  - No repeated fatal rendering errors.
  - (Current implementation may only log/fail silently; this is a gap to improve.)

### TC-UI-004: Pause analysis
- **Feature**: Pause/resume processing loop
- **Precondition**: Camera feed active
- **Steps**:
  1. Wait until result JSON appears.
  2. Click `Pause Analysis`.
  3. Observe output for ~5 seconds.
- **Expected**:
  - Button text changes to `Resume Analysis`.
  - Result updates stop while paused.

### TC-UI-005: Resume analysis
- **Feature**: Resume processing loop
- **Precondition**: Analysis paused
- **Steps**:
  1. Click `Resume Analysis`.
- **Expected**:
  - Button text returns to `Pause Analysis`.
  - Result JSON starts updating again.

### TC-UI-006: Result JSON rendered
- **Feature**: API response presentation
- **Precondition**: API is reachable
- **Steps**:
  1. Let app run for a few cycles.
- **Expected**:
  - `<pre>` panel shows JSON response.
  - Response contains keys like `ok`, `status`, `metrics`, `issues`.

---

## 2) Node API (`/health`, `/api/analyze`)

### TC-API-001: Health endpoint
- **Feature**: Liveness endpoint
- **Request**: `GET /health`
- **Expected**:
  - HTTP `200`
  - Body: `{ "ok": true }`

### TC-API-002: Missing `imageBase64`
- **Feature**: Request validation
- **Request**: `POST /api/analyze` with `{}` body
- **Expected**:
  - HTTP `400`
  - JSON error: `imageBase64 is required`

### TC-API-003: Valid base64 image request
- **Feature**: Orchestration Node -> Python
- **Request**: Valid `data:image/jpeg;base64,...`
- **Expected**:
  - HTTP `200`
  - JSON with `ok: true`
  - Includes `status`, `metrics`, `issues`, `guidance`

### TC-API-004: Invalid base64 payload
- **Feature**: Error handling for malformed input
- **Request**: `imageBase64: "not_base64"`
- **Expected**:
  - API should return non-success error response (currently likely `500` from processor path)
  - No server crash

### TC-API-005: Python process failure
- **Feature**: Child process error propagation
- **Precondition**: Temporarily break Python executable path or force Python crash
- **Expected**:
  - HTTP `500`
  - JSON `{ ok: false, error: ... }`
  - Server remains running

### TC-API-006: Temp file cleanup
- **Feature**: Temporary file lifecycle
- **Steps**:
  1. Send analyze requests repeatedly.
  2. Inspect system temp folder.
- **Expected**:
  - Temporary frame files do not accumulate indefinitely.

---

## 3) Python Processor (`analyze_image`)

### TC-PY-001: Non-existent file path
- **Input**: path that does not exist
- **Expected**:
  - `{ ok: false, error: "Image path does not exist" }`

### TC-PY-002: Undecodable image file
- **Input**: existing text file path
- **Expected**:
  - `{ ok: false, error: "Failed to decode image" }`

### TC-PY-003: Very dark image
- **Input**: near-black image
- **Expected**:
  - `ok: true`
  - `issues` includes `too_dark`
  - `status: "needs_attention"`

### TC-PY-004: Very bright image
- **Input**: near-white image
- **Expected**:
  - `ok: true`
  - `issues` includes `too_bright`
  - `status: "needs_attention"`

### TC-PY-005: Blurry/low-detail image
- **Input**: flat-color image
- **Expected**:
  - `ok: true`
  - `issues` includes `too_blurry`

### TC-PY-006: Detailed sharp image
- **Input**: high-edge synthetic checkerboard
- **Expected**:
  - `ok: true`
  - `metrics.blurScore` significantly higher than flat image
  - `too_blurry` ideally absent (threshold dependent)

---

## 4) End-to-End Flow

### TC-E2E-001: Normal user flow
- **Steps**:
  1. Start Node API.
  2. Start React UI.
  3. Allow camera access.
- **Expected**:
  - UI receives periodic analysis every ~2 seconds.
  - Values change as camera scene changes.

### TC-E2E-002: Scene quality transitions
- **Steps**:
  1. Cover camera lens (dark scene).
  2. Shine bright light into camera.
  3. Shake camera quickly.
- **Expected**:
  - Dark scene -> `too_dark`
  - Bright glare -> `too_bright`
  - Motion blur -> `too_blurry`

### TC-E2E-003: API unavailable
- **Steps**:
  1. Stop Node API while UI is open.
- **Expected**:
  - UI should not crash.
  - Network request errors appear (currently no user-friendly UI error; improvement opportunity).

---

## 5) Non-Functional Checks

### TC-NF-001: Response time
- **Goal**: Ensure analysis feels near-real-time
- **Method**: Measure `/api/analyze` response latency across 50 calls
- **Expected**: Stable latency within acceptable target for your environment

### TC-NF-002: Basic load behavior
- **Goal**: Validate service under small burst traffic
- **Method**: Send concurrent requests (e.g., 10-20)
- **Expected**:
  - No process crash
  - Predictable error handling if saturated

### TC-NF-003: Security hygiene (input size)
- **Goal**: Validate oversized payload handling
- **Method**: Send payload >5MB
- **Expected**:
  - Request rejected due to Express JSON limit
  - Server remains healthy
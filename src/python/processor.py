#!/usr/bin/env python3
"""
OpenCV best-practice demo:
- Validate input early
- Keep processing pipeline simple and measurable
- Return structured JSON for frontend/API use
"""

import cv2
import json
import os
import sys


def analyze_image(image_path: str):
    if not os.path.exists(image_path):
        return {"ok": False, "error": "Image path does not exist"}

    image = cv2.imread(image_path)
    if image is None:
        return {"ok": False, "error": "Failed to decode image"}

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Metrics often used in production pre-checks:
    # 1) Brightness: mean pixel intensity
    brightness = float(gray.mean())

    # 2) Blur score: variance of Laplacian (higher = sharper)
    blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())

    # Thresholds should be calibrated with your own camera/environment data
    too_dark = brightness < 70
    too_bright = brightness > 200
    too_blurry = blur_score < 100

    issues = []
    if too_dark:
        issues.append("too_dark")
    if too_bright:
        issues.append("too_bright")
    if too_blurry:
        issues.append("too_blurry")

    status = "good" if not issues else "needs_attention"

    return {
        "ok": True,
        "status": status,
        "metrics": {
            "brightness": round(brightness, 2),
            "blurScore": round(blur_score, 2)
        },
        "issues": issues,
        "guidance": {
            "too_dark": "Increase ambient light or move closer to a light source.",
            "too_bright": "Reduce direct glare/light intensity.",
            "too_blurry": "Hold camera steady or improve focus."
        }
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(json.dumps({"ok": False, "error": "Usage: processor.py <image_path>"}))
        sys.exit(1)

    result = analyze_image(sys.argv[1])
    print(json.dumps(result))
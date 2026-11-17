#!/usr/bin/env python3
import os
import tempfile
import unittest

import cv2
import numpy as np

from processor import analyze_image


class TestAnalyzeImage(unittest.TestCase):
    def test_nonexistent_path_returns_error(self):
        result = analyze_image("/tmp/definitely-not-existing-file.jpg")
        self.assertFalse(result["ok"])
        self.assertIn("does not exist", result["error"])

    def test_invalid_image_file_returns_decode_error(self):
        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            f.write(b"this is not an image")
            tmp_path = f.name

        try:
            result = analyze_image(tmp_path)
            self.assertFalse(result["ok"])
            self.assertIn("Failed to decode image", result["error"])
        finally:
            os.remove(tmp_path)

    def test_dark_image_flags_too_dark(self):
        dark = np.zeros((120, 160, 3), dtype=np.uint8)

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            tmp_path = f.name
        try:
            cv2.imwrite(tmp_path, dark)
            result = analyze_image(tmp_path)

            self.assertTrue(result["ok"])
            self.assertIn("too_dark", result["issues"])
            self.assertEqual(result["status"], "needs_attention")
        finally:
            os.remove(tmp_path)

    def test_bright_image_flags_too_bright(self):
        bright = np.full((120, 160, 3), 255, dtype=np.uint8)

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f:
            tmp_path = f.name
        try:
            cv2.imwrite(tmp_path, bright)
            result = analyze_image(tmp_path)

            self.assertTrue(result["ok"])
            self.assertIn("too_bright", result["issues"])
            self.assertEqual(result["status"], "needs_attention")
        finally:
            os.remove(tmp_path)

    def test_checkerboard_is_sharper_than_flat_image(self):
        flat = np.full((120, 160, 3), 127, dtype=np.uint8)

        checker = np.zeros((120, 160), dtype=np.uint8)
        tile = 10
        for y in range(0, checker.shape[0], tile):
            for x in range(0, checker.shape[1], tile):
                if ((x // tile) + (y // tile)) % 2 == 0:
                    checker[y:y + tile, x:x + tile] = 255
        checker_bgr = cv2.cvtColor(checker, cv2.COLOR_GRAY2BGR)

        with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f1, \
             tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as f2:
            flat_path = f1.name
            checker_path = f2.name

        try:
            cv2.imwrite(flat_path, flat)
            cv2.imwrite(checker_path, checker_bgr)

            flat_result = analyze_image(flat_path)
            checker_result = analyze_image(checker_path)

            self.assertTrue(flat_result["ok"])
            self.assertTrue(checker_result["ok"])

            self.assertLess(
                flat_result["metrics"]["blurScore"],
                checker_result["metrics"]["blurScore"]
            )
        finally:
            os.remove(flat_path)
            os.remove(checker_path)


if __name__ == "__main__":
    unittest.main()
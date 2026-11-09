
import os
import cv2
import mss
import numpy as np

from threading import Lock
from typing import Optional


class Vision:

    def __init__(self, monitor_index: int = 1):

        self.sct = mss.mss()
        self.monitor_index = monitor_index
        self.lock = Lock()
        self._closed = False

        monitors = self.sct.monitors

        if not isinstance(monitor_index, int):
            self.close()
            raise ValueError("Monitor index harus berupa integer.")

        if monitor_index < 1 or monitor_index >= len(monitors):
            self.close()
            raise ValueError(
                f"Monitor index {monitor_index} tidak ditemukan."
            )

        self.monitor = monitors[monitor_index]

    def capture_screen(
        self,
        region: Optional[dict] = None
    ) -> np.ndarray:

        if self._closed:
            raise RuntimeError("Vision sudah ditutup.")

        capture_area = region if region else self.monitor

        with self.lock:
            screenshot = self.sct.grab(capture_area)

        frame = np.array(screenshot)

        return cv2.cvtColor(
            frame,
            cv2.COLOR_BGRA2BGR
        )

    def load_template(self, template_path):

        if not os.path.isfile(template_path):
            print(
                f"[VISION] Template tidak ditemukan: {template_path}"
            )
            return None

        template = cv2.imread(
            template_path,
            cv2.IMREAD_GRAYSCALE
        )

        if template is None:
            print(
                f"[VISION] Gagal membaca template: {template_path}"
            )
            return None

        if template.size == 0:
            print("[VISION] Template kosong.")
            return None

        if template.shape[0] < 5 or template.shape[1] < 5:
            print("[VISION] Ukuran template terlalu kecil.")
            return None

        return template

    def match_template(
        self,
        template_path,
        threshold=0.85,
        region=None
    ):

        if not 0.0 <= threshold <= 1.0:
            raise ValueError(
                "Threshold harus antara 0.0 dan 1.0."
            )

        template = self.load_template(template_path)

        if template is None:
            return None

        frame = self.capture_screen(region)

        gray_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2GRAY
        )

        template_height, template_width = template.shape
        frame_height, frame_width = gray_frame.shape

        if (
            template_width > frame_width
            or template_height > frame_height
        ):
            print(
                "[VISION] Template lebih besar dari area layar."
            )
            return None

        result = cv2.matchTemplate(
            gray_frame,
            template,
            cv2.TM_CCOEFF_NORMED
        )

        _, max_confidence, _, max_location = cv2.minMaxLoc(
            result
        )

        if not np.isfinite(max_confidence):
            return None

        x, y = max_location

        offset_x = (
            region["left"]
            if region
            else self.monitor["left"]
        )

        offset_y = (
            region["top"]
            if region
            else self.monitor["top"]
        )

        return {
            "found": bool(max_confidence >= threshold),
            "confidence": float(max_confidence),
            "threshold": float(threshold),
            "x": int(offset_x + x + template_width // 2),
            "y": int(offset_y + y + template_height // 2),
            "left": int(offset_x + x),
            "top": int(offset_y + y),
            "width": int(template_width),
            "height": int(template_height)
        }
    
    def find_template(
        self,
        template_path,
        threshold=0.85,
        region=None
    ):

        result = self.match_template(
            template_path,
            threshold,
            region
        )

        if result is None or not result["found"]:
            return None

        return result
    
    def is_template_visible(
        self,
        template_path: str,
        threshold: float = 0.85
    ) -> bool:

        return self.find_template(
            template_path,
            threshold
        ) is not None

    def close(self):

        if not self._closed:
            with self.lock:
                self.sct.close()
                self._closed = True

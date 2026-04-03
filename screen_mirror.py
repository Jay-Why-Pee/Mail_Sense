"""Mail Sense - Screen Mirror Engine (real-time capture & change detection)"""
import numpy as np
from PIL import Image
import mss
from PyQt6.QtCore import QObject, QTimer, pyqtSignal


class ScreenMirror(QObject):
    """Captures a screen region periodically and detects when content stabilizes."""

    frame_captured = pyqtSignal(object)      # PIL Image
    screen_stabilized = pyqtSignal(object)   # PIL Image after stable period
    screen_changed = pyqtSignal(object)      # PIL Image when threshold difference detected

    def __init__(self, interval_ms=200, threshold=0.95, stable_sec=0.5):
        super().__init__()
        self._region = None
        self._interval = interval_ms
        self._threshold = threshold
        self._stable_sec = stable_sec

        self._timer = QTimer()
        self._timer.timeout.connect(self._on_tick)

        self._sct = mss.mss()
        self._prev_frame = None
        self._stable_count = 0
        self._stable_triggered = False
        self._running = False

    def set_region(self, x, y, w, h):
        self._region = {'left': x, 'top': y, 'width': w, 'height': h}
        self._prev_frame = None
        self._stable_count = 0
        self._stable_triggered = False

    def start(self):
        if self._region:
            self._running = True
            self._timer.start(self._interval)

    def stop(self):
        self._running = False
        self._timer.stop()

    def is_running(self):
        return self._running

    def capture_once(self):
        if not self._region:
            return None
        try:
            shot = self._sct.grab(self._region)
            return Image.frombytes('RGB', shot.size, shot.bgra, 'raw', 'BGRX')
        except Exception:
            return None

    def reset_stability(self):
        self._stable_count = 0
        self._stable_triggered = False
        self._prev_frame = None

    def _on_tick(self):
        if not self._region:
            return
        try:
            shot = self._sct.grab(self._region)
            img = Image.frombytes('RGB', shot.size, shot.bgra, 'raw', 'BGRX')
            self.frame_captured.emit(img)

            if self._prev_frame is not None:
                if self._similar(self._prev_frame, img):
                    self._stable_count += 1
                    needed = int(self._stable_sec * 1000 / self._interval)
                    if self._stable_count >= needed and not self._stable_triggered:
                        self._stable_triggered = True
                        self.screen_stabilized.emit(img)
                else:
                    self._stable_count = 0
                    self._stable_triggered = False
                    self.screen_changed.emit(img)
            self._prev_frame = img
        except Exception:
            pass

    def _similar(self, a, b):
        try:
            a1 = np.array(a.convert('L'), dtype=np.float32)
            a2 = np.array(b.convert('L'), dtype=np.float32)
            if a1.shape != a2.shape:
                return False
            mse = np.mean((a1 - a2) ** 2)
            return (1.0 - mse / 65025.0) > self._threshold
        except Exception:
            return False

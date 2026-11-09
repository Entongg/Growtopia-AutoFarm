
import threading
import time
from typing import Optional, Callable

from core.input_manager import InputManager


class AutoPunch:

    def __init__(
        self,
        input_manager: InputManager,
        dry_run: bool = True,
        status_callback: Optional[Callable] = None
    ):
        self.input_manager = input_manager
        self.dry_run = dry_run
        self.status_callback = status_callback

        self.stop_event = threading.Event()
        self.pause_event = threading.Event()

        self.thread = None
        self.lock = threading.Lock()

        self.running = False
        self.click_count = 0

    def _notify(self, message: str):
        print(f"[AUTO PUNCH] {message}")

        if self.status_callback:
            try:
                self.status_callback(message)
            except Exception as error:
                print(f"[AUTO PUNCH] Callback error: {error}")

    def is_running(self) -> bool:
        with self.lock:
            return self.running

    def _wait_if_paused(self, start_time):
        while self.pause_event.is_set():

            pause_start = time.monotonic()

            while self.pause_event.is_set():
                if self.stop_event.wait(0.05):
                    return None

            start_time += time.monotonic() - pause_start

            self._notify("Melanjutkan Auto Punch.")

        if self.stop_event.is_set():
            return None

        return start_time

    def _wait_interval(self, duration: float, start_time):
        deadline = time.monotonic() + duration

        while time.monotonic() < deadline:

            if self.stop_event.is_set():
                return start_time

            if self.pause_event.is_set():

                pause_start = time.monotonic()

                while self.pause_event.is_set():
                    if self.stop_event.wait(0.05):
                        return start_time

                paused_duration = time.monotonic() - pause_start

                deadline += paused_duration
                start_time += paused_duration

                self._notify("Melanjutkan Auto Punch.")

            else:
                remaining = deadline - time.monotonic()
                self.stop_event.wait(min(0.05, remaining))

        return start_time

    def start(
        self,
        x: int,
        y: int,
        interval: float = 0.5,
        max_duration: float = 30.0,
        max_actions: int = 100,
        pause_event=None
    ) -> bool:

        if x < 0 or y < 0:
            raise ValueError("Koordinat tidak boleh negatif.")

        if interval <= 0:
            raise ValueError("Interval harus lebih besar dari 0.")

        if max_duration <= 0:
            raise ValueError("Durasi harus lebih besar dari 0.")

        if max_actions < 1:
            raise ValueError("Jumlah aksi minimal 1.")

        with self.lock:

            if self.running:
                return False

            if self.thread and self.thread.is_alive():
                return False

            self.stop_event.clear()
            self.pause_event = (
                pause_event if pause_event is not None
                else threading.Event()
            )

            self.click_count = 0
            self.running = True

            self.thread = threading.Thread(
                target=self._run,
                args=(x, y, interval, max_duration, max_actions),
                daemon=True
            )

            self.thread.start()

        mode = "SIMULASI" if self.dry_run else "AKTIF"

        self._notify(
            f"Dimulai | Mode: {mode} | Target: ({x}, {y})"
        )

        return True

    def _run(
        self,
        x,
        y,
        interval,
        max_duration,
        max_actions
    ):

        start_time = time.monotonic()

        try:

            while not self.stop_event.is_set():

                start_time = self._wait_if_paused(start_time)

                if start_time is None:
                    break

                elapsed = time.monotonic() - start_time

                if elapsed >= max_duration:
                    self._notify("Batas durasi tercapai.")
                    break

                if self.click_count >= max_actions:
                    self._notify("Batas jumlah aksi tercapai.")
                    break

                if self.dry_run:
                    self._notify(
                        f"Simulasi klik ke ({x}, {y})"
                    )
                else:
                    success = self.input_manager.click(
                        x=x,
                        y=y,
                        button="left"
                    )

                    if not success:
                        self._notify("Input dihentikan.")
                        break

                self.click_count += 1

                remaining = max(
                    0.0,
                    interval - self.input_manager.interval
                )

                start_time = self._wait_interval(
                    remaining,
                    start_time
                )

        except Exception as error:
            self._notify(f"Terjadi kesalahan: {error}")

        finally:

            self.input_manager.release_all()

            with self.lock:
                self.running = False

            self._notify(
                f"Selesai. Total aksi: {self.click_count}"
            )

    def pause(self):
        if self.is_running():
            self.pause_event.set()
            self.input_manager.release_all()
            return True
        return False

    def resume(self):
        self.pause_event.clear()

    def stop(self):

        self.stop_event.set()
        self.pause_event.clear()

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2.0)

        self.input_manager.release_all()
        self._notify("Perintah berhenti dikirim.")

    def get_click_count(self) -> int:
        with self.lock:
            return self.click_count

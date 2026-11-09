import threading
import time
from typing import Callable, Optional


class ReconnectMonitor:
    """
    Memantau status koneksi berdasarkan fungsi deteksi visual.

    Tidak melakukan login atau mengirim input ke game.
    Hanya mendeteksi perubahan status dan memberikan notifikasi.
    """

    def __init__(
        self,
        detect_disconnected: Callable[[], bool],
        detect_connected: Callable[[], bool],
        callback: Optional[Callable[[str], None]] = None,
        interval: float = 2.0,
        confirm_count: int = 2
    ):
        if interval <= 0:
            raise ValueError("Interval harus lebih dari 0.")

        if confirm_count < 1:
            raise ValueError("Confirm count minimal 1.")

        self.detect_disconnected = detect_disconnected
        self.detect_connected = detect_connected
        self.callback = callback

        self.interval = interval
        self.confirm_count = confirm_count

        self._stop_event = threading.Event()
        self._thread = None
        self._lock = threading.RLock()

        self._running = False
        self._status = "unknown"

        self._disconnected_count = 0
        self._connected_count = 0

    def start(self):
        """Memulai pemantauan koneksi."""

        with self._lock:
            if self._running:
                return False

            self._stop_event.clear()
            self._running = True

            self._thread = threading.Thread(
                target=self._monitor,
                daemon=True,
                name="ReconnectMonitor"
            )

            self._thread.start()

        self._notify("Pemantauan koneksi dimulai.")
        return True

    def stop(self):
        """Menghentikan pemantauan koneksi."""

        self._stop_event.set()

        with self._lock:
            thread = self._thread

        if thread and thread.is_alive():
            if thread is not threading.current_thread():
                thread.join(timeout=3)

        with self._lock:
            if thread is None or not thread.is_alive():
                self._running = False
                self._thread = None

        self._notify("Pemantauan koneksi dihentikan.")

    def get_status(self):
        """Mengambil status koneksi saat ini."""

        with self._lock:
            return self._status

    def is_running(self):
        with self._lock:
            return self._running

    def _monitor(self):
        try:
            while not self._stop_event.is_set():
                try:
                    disconnected = self.detect_disconnected()
                    connected = self.detect_connected()

                    self._process_detection(
                        disconnected=disconnected,
                        connected=connected
                    )

                except Exception as error:
                    self._notify(
                        f"Kesalahan saat mendeteksi koneksi: {error}"
                    )

                self._stop_event.wait(self.interval)

        finally:
            with self._lock:
                self._running = False
                self._thread = None

    def _process_detection(self, disconnected, connected):
        new_status = None

        with self._lock:
            if disconnected:
                self._disconnected_count += 1
                self._connected_count = 0

                if self._disconnected_count >= self.confirm_count:
                    new_status = "disconnected"

            elif connected:
                self._connected_count += 1
                self._disconnected_count = 0

                if self._connected_count >= self.confirm_count:
                    new_status = "connected"

            else:
                self._disconnected_count = 0
                self._connected_count = 0

            if new_status and new_status != self._status:
                self._status = new_status
            else:
                new_status = None

        if new_status == "disconnected":
            self._notify(
                "Koneksi terputus. Silakan periksa game dan pulihkan "
                "koneksi secara manual."
            )

        elif new_status == "connected":
            self._notify("Koneksi terdeteksi kembali.")

    def _notify(self, message):
        if self.callback:
            try:
                self.callback(message)
            except Exception as error:
                print(f"Callback error: {error}")
        else:
            print(f"[Reconnect Monitor] {message}")

    def close(self):
        self.stop()

import time
import threading
import pyautogui


class InputManager:
    """
    Mengelola input keyboard dan mouse.

    Fitur:
    - Klik mouse kiri dan kanan.
    - Menekan dan melepas tombol keyboard.
    - Menahan tombol keyboard dan mouse.
    - Mengatur jeda input.
    - Menghentikan input melalui stop().
    - Melepas seluruh tombol ketika dihentikan.
    """

    def __init__(self, interval: float = 0.05):
        self.interval = max(0.0, interval)

        self.stop_event = threading.Event()
        self.lock = threading.RLock()

        self.held_keys = set()
        self.held_mouse_buttons = set()

        # PyAutoGUI akan memicu fail-safe jika cursor
        # dipindahkan ke sudut kiri atas layar.
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.02

    def _can_run(self) -> bool:
        """Memeriksa apakah input masih diizinkan."""
        return not self.stop_event.is_set()

    def _wait(self, duration: float = None) -> bool:
        """Jeda yang dapat diputus ketika sistem dihentikan."""
        delay = self.interval if duration is None else max(0.0, duration)

        if delay == 0:
            return self._can_run()

        return not self.stop_event.wait(delay)

    def get_mouse_position(self) -> tuple:
        """Mengambil posisi cursor saat ini."""
        position = pyautogui.position()
        return position.x, position.y

    def move_to(
        self,
        x: int,
        y: int,
        duration: float = 0.1
    ) -> bool:
        """Memindahkan cursor ke koordinat tertentu."""
        if not self._can_run():
            return False

        with self.lock:
            if not self._can_run():
                return False

            pyautogui.moveTo(
                x,
                y,
                duration=max(0.0, duration)
            )

        return True

    def click(
        self,
        x: int = None,
        y: int = None,
        button: str = "left",
        clicks: int = 1,
        interval: float = 0.1
    ) -> bool:
        """Melakukan klik mouse."""
        if not self._can_run():
            return False

        if button not in ("left", "right", "middle"):
            raise ValueError("Button harus left, right, atau middle.")

        if clicks < 1:
            raise ValueError("Clicks minimal 1.")

        with self.lock:
            if not self._can_run():
                return False

            pyautogui.click(
                x=x,
                y=y,
                clicks=clicks,
                interval=max(0.0, interval),
                button=button
            )

        return self._wait()

    def mouse_down(self, button: str = "left") -> bool:
        """Menahan tombol mouse."""
        if not self._can_run():
            return False

        if button not in ("left", "right", "middle"):
            raise ValueError("Button mouse tidak valid.")

        with self.lock:
            if not self._can_run():
                return False

            pyautogui.mouseDown(button=button)
            self.held_mouse_buttons.add(button)

        return True

    def mouse_up(self, button: str = "left") -> bool:
        """Melepas tombol mouse."""
        with self.lock:
            pyautogui.mouseUp(button=button)
            self.held_mouse_buttons.discard(button)

        return True

    def key_down(self, key: str) -> bool:
        """Menahan tombol keyboard."""
        if not self._can_run():
            return False

        with self.lock:
            if not self._can_run():
                return False

            pyautogui.keyDown(key)
            self.held_keys.add(key)

        return True

    def key_up(self, key: str) -> bool:
        """Melepas tombol keyboard."""
        with self.lock:
            pyautogui.keyUp(key)
            self.held_keys.discard(key)

        return True

    def press(
        self,
        key: str,
        presses: int = 1,
        interval: float = 0.1
    ) -> bool:
        """Menekan tombol keyboard sebanyak jumlah tertentu."""
        if not self._can_run():
            return False

        if presses < 1:
            raise ValueError("Presses minimal 1.")

        for _ in range(presses):
            if not self._can_run():
                return False

            with self.lock:
                if not self._can_run():
                    return False

                pyautogui.press(key)

            if not self._wait(interval):
                return False

        return True

    def hold_key(self, key: str, duration: float) -> bool:
        """Menahan tombol selama durasi tertentu."""
        if duration < 0:
            raise ValueError("Duration tidak boleh negatif.")

        if not self.key_down(key):
            return False

        try:
            return self._wait(duration)
        finally:
            self.key_up(key)

    def release_all(self):
        """Melepas semua tombol yang tercatat sedang ditahan."""
        with self.lock:
            for key in list(self.held_keys):
                try:
                    pyautogui.keyUp(key)
                except Exception:
                    pass

            for button in list(self.held_mouse_buttons):
                try:
                    pyautogui.mouseUp(button=button)
                except Exception:
                    pass

            self.held_keys.clear()
            self.held_mouse_buttons.clear()

    def stop(self):
        """Menghentikan input dan melepas semua tombol."""
        self.stop_event.set()
        self.release_all()

    def reset(self):
        """Mengaktifkan kembali Input Manager setelah dihentikan."""
        self.release_all()
        self.stop_event.clear()

    def close(self):
        """Menutup Input Manager."""
        self.stop()

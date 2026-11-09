
import threading
from typing import Optional, Callable

from core.input_manager import InputManager
from features.auto_punch import AutoPunch
from features.auto_put import AutoPut


class FarmLoop:

    def __init__(
        self,
        auto_punch: AutoPunch,
        auto_put: AutoPut,
        input_manager: InputManager,
        status_callback: Optional[Callable] = None
    ):

        self.auto_punch = auto_punch
        self.auto_put = auto_put
        self.input_manager = input_manager
        self.status_callback = status_callback

        self.stop_event = threading.Event()
        self.pause_event = threading.Event()

        self.lock = threading.Lock()

        self.thread = None
        self.running = False
        self.cycles_completed = 0

    def _notify(self, message: str):

        print(f"[FARM LOOP] {message}")

        if self.status_callback:
            try:
                self.status_callback(message)
            except Exception as error:
                print(f"[FARM LOOP] Callback error: {error}")

    def is_running(self) -> bool:
        with self.lock:
            return self.running

    def is_paused(self) -> bool:
        return self.pause_event.is_set()

    def get_cycles_completed(self) -> int:
        with self.lock:
            return self.cycles_completed

    def _wait_for_feature(self, feature) -> bool:

        while feature.is_running():

            if self.stop_event.wait(0.05):
                feature.stop()
                return False

        return not self.stop_event.is_set()

    def start(
        self,
        punch_config: dict,
        put_config: dict,
        cycles: int = 1
    ) -> bool:

        if not isinstance(cycles, int) or cycles < 1:
            raise ValueError(
                "Cycles harus berupa integer minimal 1."
            )

        if not isinstance(punch_config, dict):
            raise TypeError(
                "punch_config harus berupa dictionary."
            )

        if not isinstance(put_config, dict):
            raise TypeError(
                "put_config harus berupa dictionary."
            )

        with self.lock:

            if self.running:
                self._notify("Farm Loop sudah berjalan.")
                return False

            if self.thread and self.thread.is_alive():
                return False

            if (
                self.auto_punch.is_running()
                or self.auto_put.is_running()
            ):
                self._notify("Fitur lain masih berjalan.")
                return False

            self.stop_event.clear()
            self.pause_event.clear()

            self.cycles_completed = 0
            self.running = True

            self.thread = threading.Thread(
                target=self._run,
                args=(
                    punch_config.copy(),
                    put_config.copy(),
                    cycles
                ),
                daemon=True
            )

            self.thread.start()

        self._notify("Farm Loop dimulai.")
        return True

    def _run(
        self,
        punch_config: dict,
        put_config: dict,
        cycles: int
    ):

        try:

            # Satu pause_event dipakai oleh kedua fitur.
            punch_config["pause_event"] = self.pause_event
            put_config["pause_event"] = self.pause_event

            for cycle in range(1, cycles + 1):

                if self.stop_event.is_set():
                    break

                self._notify(
                    f"Siklus {cycle}/{cycles}"
                )

                self._notify("Menjalankan Auto Punch...")

                started = self.auto_punch.start(
                    **punch_config
                )

                if not started:
                    self._notify(
                        "Auto Punch gagal dimulai."
                    )
                    break

                if not self._wait_for_feature(
                    self.auto_punch
                ):
                    break

                if self.stop_event.is_set():
                    break

                self._notify("Menjalankan Auto Put...")

                started = self.auto_put.start(
                    **put_config
                )

                if not started:
                    self._notify(
                        "Auto Put gagal dimulai."
                    )
                    break

                if not self._wait_for_feature(
                    self.auto_put
                ):
                    break

                if self.stop_event.is_set():
                    break

                with self.lock:
                    self.cycles_completed += 1

                self._notify(
                    f"Siklus {cycle} selesai."
                )

        except Exception as error:

            self._notify(
                f"Terjadi kesalahan: {error}"
            )

        finally:

            self.pause_event.clear()
            self.input_manager.release_all()

            with self.lock:
                self.running = False

            self._notify(
                "Farm Loop selesai. "
                f"Total siklus: {self.get_cycles_completed()}"
            )

    def pause(self):

        if not self.is_running():
            self._notify(
                "Farm Loop tidak sedang berjalan."
            )
            return False

        if self.pause_event.is_set():
            self._notify(
                "Farm Loop sudah dalam keadaan Pause."
            )
            return False

        self.pause_event.set()

        self.input_manager.release_all()

        self._notify(
            "Farm Loop dijeda."
        )

        return True

    def resume(self):

        if not self.is_running():
            self._notify(
                "Farm Loop tidak sedang berjalan."
            )
            return False

        if not self.pause_event.is_set():
            self._notify(
                "Farm Loop tidak sedang dijeda."
            )
            return False

        self.pause_event.clear()

        self._notify(
            "Farm Loop dilanjutkan."
        )

        return True

    def stop(self):

        self.stop_event.set()
        self.pause_event.clear()

        self.auto_punch.stop()
        self.auto_put.stop()

        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=3.0)

        self.input_manager.release_all()

        self._notify(
            "Perintah berhenti dikirim."
        )

    def close(self):
        self.stop()

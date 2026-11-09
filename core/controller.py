from pathlib import Path

from core.input_manager import InputManager
from core.farm_loop import FarmLoop
from core.reconnect import ReconnectMonitor
from core.vision import Vision

from features.auto_punch import AutoPunch
from features.auto_put import AutoPut


BASE_DIR = Path(__file__).resolve().parent.parent


class AppController:

    def __init__(
        self,
        notification_callback=None,
        config_data=None
    ):

        self.notification_callback = notification_callback
        self.config_data = config_data or {}

        self.input_manager = InputManager(interval=0)

        self.auto_punch = AutoPunch(
            input_manager=self.input_manager,
            dry_run=True
        )

        self.auto_put = AutoPut(
            input_manager=self.input_manager,
            dry_run=True
        )

        self.farm_loop = FarmLoop(
            auto_punch=self.auto_punch,
            auto_put=self.auto_put,
            input_manager=self.input_manager
        )

        self.vision = None
        self.reconnect_monitor = None

        self._initialize_vision()

        reconnect_config = self.config_data.get(
            "reconnect", {}
        )

        if reconnect_config.get("enabled", False):
            self.start_reconnect_monitor()

        self._notify("Controller berhasil diinisialisasi.")

    def _notify(self, message):

        if self.notification_callback:
            self.notification_callback(message)
        else:
            print(f"[Controller] {message}")

    def _resolve_path(self, path):

        path = Path(path)

        if not path.is_absolute():
            path = BASE_DIR / path

        return path

    def _initialize_vision(self):

        vision_config = self.config_data.get(
            "vision", {}
        )

        monitor_index = vision_config.get(
            "monitor_index", 1
        )

        threshold = vision_config.get(
            "threshold", 0.85
        )

        connected_path = self._resolve_path(
            vision_config.get(
                "connected_template",
                "assets/templates/connected.png"
            )
        )

        disconnected_path = self._resolve_path(
            vision_config.get(
                "disconnected_template",
                "assets/templates/disconnected.png"
            )
        )

        try:

            self.vision = Vision(
                monitor_index=monitor_index
            )

            self._notify(
                f"Vision menggunakan monitor {monitor_index}."
            )

            if not connected_path.is_file():
                self._notify(
                    f"Template tidak ditemukan: {connected_path}"
                )

            if not disconnected_path.is_file():
                self._notify(
                    f"Template tidak ditemukan: {disconnected_path}"
                )

            if (
                not connected_path.is_file()
                or not disconnected_path.is_file()
            ):
                self._notify(
                    "Reconnect belum disiapkan karena template belum lengkap."
                )
                return

            reconnect_config = self.config_data.get(
                "reconnect", {}
            )

            interval = reconnect_config.get(
                "interval", 2.0
            )

            confirm_count = reconnect_config.get(
                "confirm_count", 2
            )

            self.reconnect_monitor = ReconnectMonitor(
                detect_disconnected=lambda: (
                    self.vision.find_template(
                        str(disconnected_path),
                        threshold=threshold
                    ) is not None
                ),
                detect_connected=lambda: (
                    self.vision.find_template(
                        str(connected_path),
                        threshold=threshold
                    ) is not None
                ),
                callback=self._notify,
                interval=interval,
                confirm_count=confirm_count
            )

            self._notify(
                "Vision dan Reconnect berhasil disiapkan."
            )

        except Exception as error:

            self._notify(
                f"Gagal menginisialisasi Vision: {error}"
            )

            if self.vision:
                self.vision.close()
                self.vision = None

            self.reconnect_monitor = None

    def apply_config(self, config_data):
        """
        Menerapkan konfigurasi terbaru dari Dashboard.

        Pemantauan Reconnect dihentikan terlebih dahulu agar
        Vision tidak ditutup ketika masih digunakan thread.
        """

        if self.farm_loop.is_running():
            self._notify(
                "Hentikan Farm Loop sebelum menerapkan konfigurasi."
            )
            return False

        self.stop_reconnect_monitor()

        if (
            self.reconnect_monitor
            and self.reconnect_monitor.is_running()
        ):
            self._notify(
                "Reconnect masih berjalan. Konfigurasi belum diterapkan."
            )
            return False

        if self.vision:
            self.vision.close()
            self.vision = None

        self.reconnect_monitor = None
        self.config_data = config_data or {}

        self._initialize_vision()

        reconnect_config = self.config_data.get(
            "reconnect", {}
        )

        if reconnect_config.get("enabled", False):
            return self.start_reconnect_monitor()

        self._notify(
            "Konfigurasi berhasil diterapkan. Monitoring Reconnect nonaktif."
        )

        return True

    def start_farm(
        self,
        punch_config,
        put_config,
        cycles=1
    ):

        if self.farm_loop.is_running():
            self._notify("Farm Loop sedang berjalan.")
            return False

        try:

            result = self.farm_loop.start(
                punch_config=punch_config,
                put_config=put_config,
                cycles=cycles
            )

            if result is not False:
                self._notify("Farm Loop dimulai.")

            return result

        except Exception as error:

            self._notify(
                f"Gagal memulai Farm Loop: {error}"
            )
            return False

    def stop_farm(self):

        try:

            self.farm_loop.stop()
            self._notify("Farm Loop dihentikan.")
            return True

        except Exception as error:

            self._notify(
                f"Gagal menghentikan Farm Loop: {error}"
            )
            return False

    def pause_farm(self):
        if not self.farm_loop.is_running():
            self._notify("Farm Loop tidak sedang berjalan.")
            return False

        if self.farm_loop.is_paused():
            self._notify("Farm Loop sudah dijeda.")
            return False

        try:
            result = self.farm_loop.pause()

            if result:
                self._notify("Farm Loop berhasil dijeda.")

            return result

        except Exception as error:
            self._notify(f"Gagal menjeda Farm Loop: {error}")
            return False

    def resume_farm(self):
        if not self.farm_loop.is_running():
            self._notify("Farm Loop tidak sedang berjalan.")
            return False

        if not self.farm_loop.is_paused():
            self._notify("Farm Loop tidak dalam kondisi Pause.")
            return False

        try:
            result = self.farm_loop.resume()

            if result:
                self._notify("Farm Loop dilanjutkan.")

            return result

        except Exception as error:
            self._notify(f"Gagal melanjutkan Farm Loop: {error}")
            return False

    def is_farm_paused(self):
        return self.farm_loop.is_paused()

    def get_reconnect_status(self):

        if not self.reconnect_monitor:
            return "not_configured"

        return self.reconnect_monitor.get_status()

    def start_reconnect_monitor(self):

        if not self.reconnect_monitor:
            self._notify(
                "Reconnect belum siap. Periksa monitor dan template Vision."
            )
            return False

        return self.reconnect_monitor.start()

    def stop_reconnect_monitor(self):

        if self.reconnect_monitor:
            self.reconnect_monitor.stop()

    def get_farm_status(self):
        return self.farm_loop.is_running()

    def get_cycle_count(self):
        return self.farm_loop.get_cycles_completed()

    def test_template(self, template_name):

        if not self.vision:
            raise RuntimeError(
                "Vision belum tersedia. Periksa konfigurasi monitor."
            )

        vision_config = self.config_data.get("vision", {})

        template_options = {
            "Connected": vision_config.get(
                "connected_template",
                "assets/templates/connected.png"
            ),
            "Disconnected": vision_config.get(
                "disconnected_template",
                "assets/templates/disconnected.png"
            )
        }

        if template_name not in template_options:
            raise ValueError("Jenis template tidak dikenal.")

        template_path = self._resolve_path(
            template_options[template_name]
        )

        if not template_path.is_file():
            raise FileNotFoundError(
                f"Template tidak ditemukan: {template_path}"
            )

        threshold = float(
            vision_config.get("threshold", 0.85)
        )

        result = self.vision.match_template(
            str(template_path),
            threshold=threshold
        )

        if result is None:
            raise RuntimeError(
                "Template gagal dibaca atau ukuran template tidak sesuai layar."
            )

        return result

    def close(self):

        self._notify("Menutup seluruh modul...")

        try:
            self.stop_farm()
        finally:
            self.stop_reconnect_monitor()

            if (
                self.reconnect_monitor
                and self.reconnect_monitor.is_running()
            ):
                self._notify(
                    "Reconnect masih berjalan. Vision tidak ditutup untuk menghindari konflik."
                )
            else:
                if self.vision:
                    self.vision.close()
                    self.vision = None

            self.input_manager.release_all()
            self.input_manager.close()

        self._notify("Controller berhasil ditutup.")
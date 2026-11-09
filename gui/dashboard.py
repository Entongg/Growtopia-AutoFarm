
import tkinter as tk
import customtkinter as ctk
import queue

from datetime import datetime
from tkinter import messagebox

from config import APP_NAME, APP_VERSION

from core.state_manager import (
    StateManager,
    BotStatus
)

from gui.farm_settings import (
    FarmSettingsWindow,
    ensure_farm_config
)

from gui.vision_settings import (
    VisionSettingsWindow,
    ensure_vision_config
)

from gui.reconnect_settings import (
    ReconnectSettingsWindow,
    ensure_reconnect_config
)

from gui.activity_logs import ActivityLogsWindow
from gui.vision_testing import VisionTestingWindow

from gui.components import MetricCard
from gui.settings import load_config, save_config
from utils.logger import get_logger
from utils.validation import FarmConfigValidator

from core.controller import AppController


class AutoFarmApp(ctk.CTk):

    def __init__(self):

        super().__init__()

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title(APP_NAME)

        self.geometry("1180x760")
        self.minsize(980, 650)

        self.configure(fg_color="#0B1424")

        self.config_data = ensure_farm_config(
             load_config()     
        )

        self.config_data = ensure_vision_config(
             self.config_data
        )

        self.config_data = ensure_reconnect_config(
             self.config_data
        )

        save_config(self.config_data)

        self.state_manager = StateManager()

        self.logger = get_logger()

        self.log_queue = queue.Queue()
        self.controller = AppController(
            notification_callback=self.log,
            config_data=self.config_data
        )

        self.feature_vars = {
            "Auto Punch": tk.BooleanVar(value=False),
            "Auto Put": tk.BooleanVar(value=False),
            "Auto Farm Loop": tk.BooleanVar(value=False),
            "Auto Reconnect": tk.BooleanVar(
                value=self.config_data["reconnect"]["enabled"]
            )
        }

        self.build_layout()

        self.log("Dashboard berhasil dimuat.")

        self.after(150, self.drain_logs)

        self.after(500, self.update_dashboard_status)
    
        self.protocol(
            "WM_DELETE_WINDOW",
            self.on_close
        )

    def build_layout(self):

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # SIDEBAR

        sidebar = ctk.CTkFrame(
            self,
            width=220,
            corner_radius=0,
            fg_color="#101D30"
        )

        sidebar.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        sidebar.grid_propagate(False)

        ctk.CTkLabel(
            sidebar,
            text="GROWTOPIA",
            font=("Arial", 23, "bold"),
            text_color="#60A5FA"
        ).pack(
            anchor="w",
            padx=22,
            pady=(28, 2)
        )

        ctk.CTkLabel(
            sidebar,
            text="AUTO FARM PC",
            text_color="#8192AA"
        ).pack(
            anchor="w",
            padx=23,
            pady=(0, 28)
        )

        pages = [
            "Dashboard",
            "Farm Settings",
            "Vision Settings",
            "Vision Testing",
            "Reconnect Settings",
            "Activity Logs",
            "About"
        ]

        for page in pages:

            ctk.CTkButton(
                sidebar,
                text=page,
                anchor="w",
                height=40,
                fg_color="#1D3554" if page == "Dashboard" else "transparent",
                hover_color="#203B5E",
                command=lambda p=page: self.navigate(p)
            ).pack(
                fill="x",
                padx=12,
                pady=3
            )

        # MAIN CONTENT

        content = ctk.CTkFrame(
            self,
            fg_color="transparent"
        )

        content.grid(
            row=0,
            column=1,
            sticky="nsew",
            padx=28,
            pady=24
        )

        content.grid_columnconfigure(
            (0, 1, 2),
            weight=1
        )

        content.grid_rowconfigure(4, weight=1)

        # HEADER

        ctk.CTkLabel(
            content,
            text="Dashboard",
            font=("Arial", 28, "bold"),
            text_color="#F1F5F9"
        ).grid(
            row=0,
            column=0,
            columnspan=3,
            sticky="w",
            pady=(0, 5)
        )

        # METRICS

        self.status_card = MetricCard(
            content,
            "BOT STATUS",
            "IDLE",
            "#FBBF24"
        )

        self.status_card.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=(0, 10),
            pady=16
        )

        self.cycle_card = MetricCard(
            content,
            "FARM CYCLE",
            "0",
            "#60A5FA"
        )

        self.cycle_card.grid(
            row=1,
            column=1,
            sticky="ew",
            padx=5,
            pady=16
        )

        self.connection_card = MetricCard(
            content,
            "CONNECTION",
            "NOT CHECKED",
            "#94A3B8"
        )

        self.connection_card.grid(
            row=1,
            column=2,
            sticky="ew",
            padx=(10, 0),
            pady=16
        )

        # BOT CONTROLS

        controls = ctk.CTkFrame(
            content,
            corner_radius=14,
            fg_color="#142238"
        )

        controls.grid(
            row=2,
            column=0,
            columnspan=3,
            sticky="ew",
            pady=10
        )

        ctk.CTkLabel(
            controls,
            text="Bot Controls",
            font=("Arial", 16, "bold")
        ).pack(
            anchor="w",
            padx=18,
            pady=14
        )

        button_frame = ctk.CTkFrame(
            controls,
            fg_color="transparent"
        )

        button_frame.pack(
            fill="x",
            padx=14,
            pady=(0, 15)
        )

        buttons = [
            ("Start Bot", "#2563EB", self.start_bot),
            ("Pause Bot", "#B7791F", self.pause_bot),
            ("Resume Bot", "#16845B", self.resume_bot),
            ("Stop Bot", "#B83232", self.stop_bot)
        ]

        for label, color, command in buttons:

            ctk.CTkButton(
                button_frame,
                text=label,
                fg_color=color,
                hover_color=color,
                command=command,
                height=38
            ).pack(
                side="left",
                padx=4,
                expand=True,
                fill="x"
            )

        # FEATURE SWITCHES

        features = ctk.CTkFrame(
            content,
            corner_radius=14,
            fg_color="#142238"
        )

        features.grid(
            row=3,
            column=0,
            columnspan=3,
            sticky="ew",
            pady=10
        )

        ctk.CTkLabel(
            features,
            text="Feature Switches",
            font=("Arial", 16, "bold")
        ).pack(
            anchor="w",
            padx=18,
            pady=12
        )

        switch_frame = ctk.CTkFrame(
            features,
            fg_color="transparent"
        )

        switch_frame.pack(
            fill="x",
            padx=14,
            pady=(0, 12)
        )

        for name, variable in self.feature_vars.items():

            ctk.CTkSwitch(
                switch_frame,
                text=name,
                variable=variable,
                command=lambda n=name: self.toggle_feature(n)
            ).pack(
                side="left",
                padx=12
            )

        # ACTIVITY LOGS

        logs_frame = ctk.CTkFrame(
            content,
            corner_radius=14,
            fg_color="#142238"
        )

        logs_frame.grid(
            row=4,
            column=0,
            columnspan=3,
            sticky="nsew"
        )

        logs_frame.grid_columnconfigure(0, weight=1)
        logs_frame.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(
            logs_frame,
            text="Activity Logs",
            font=("Arial", 16, "bold")
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=18,
            pady=12
        )

        self.log_box = ctk.CTkTextbox(
            logs_frame,
            fg_color="#0C1728",
            text_color="#C7D4E5"
        )

        self.log_box.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=14,
            pady=(0, 14)
        )

        self.log_box.configure(state="disabled")

    # LOGGING

    def log(self, message):

        timestamp = datetime.now().strftime("%H:%M:%S")

        self.logger.info(message)

        self.log_queue.put(
            f"[{timestamp}] {message}"
        )

    def drain_logs(self):

        try:

            while True:

                message = self.log_queue.get_nowait()

                self.log_box.configure(state="normal")

                self.log_box.insert(
                    "end",
                    message + "\n"
                )

                self.log_box.see("end")

                self.log_box.configure(state="disabled")

        except queue.Empty:
            pass

        self.after(150, self.drain_logs)

    # BOT CONTROL

    def refresh_status(self):
        self.status_card.set_value(
            self.state_manager.status.value.upper()
        )

        self.cycle_card.set_value(
            self.controller.get_cycle_count()
        )

        reconnect_status = self.controller.get_reconnect_status()

        if reconnect_status == "connected":
            self.connection_card.set_value("CONNECTED")

        elif reconnect_status == "disconnected":
            self.connection_card.set_value("DISCONNECTED")

        elif reconnect_status == "not_configured":
            self.connection_card.set_value("NOT CONFIGURED")

        else:
            self.connection_card.set_value("UNKNOWN")

    def start_bot(self):

        # Pastikan semua fitur yang diperlukan aktif.
        if not self.feature_vars["Auto Farm Loop"].get():
            self.log("Aktifkan Auto Farm Loop terlebih dahulu.")
            return

        if not self.feature_vars["Auto Punch"].get():
            self.log("Aktifkan Auto Punch terlebih dahulu.")
            return

        if not self.feature_vars["Auto Put"].get():
            self.log("Aktifkan Auto Put terlebih dahulu.")
            return

        if not self.state_manager.start():
            self.log("Bot sudah aktif atau tidak dapat dimulai.")
            return

        # Ambil konfigurasi dari Farm Settings.
        farm_config = self.config_data["farm"]

        punch_config = dict(
            farm_config["auto_punch"]
        )

        put_config = dict(
            farm_config["auto_put"]
        )

        # JSON menggunakan list, sedangkan Farm Loop
        # menerima koordinat dalam bentuk tuple.
        put_config["positions"] = [
            tuple(position)
            for position in put_config["positions"]
        ]

        cycles = farm_config["cycles"]

        errors = FarmConfigValidator.validate(
            punch_config,
            put_config,
            cycles
        )

        if errors:

            for error in errors:
                self.log(f"Validasi gagal: {error}")

            messagebox.showerror(
                "Konfigurasi Tidak Valid",
                "\n".join(errors)
            )

            self.state_manager.stop()
            self.state_manager.mark_stopped()

            return

        self.log("Menjalankan Farm Loop dengan konfigurasi tersimpan.")

        result = self.controller.start_farm(
            punch_config=punch_config,
            put_config=put_config,
            cycles=cycles
        )

        if result is False:

            self.state_manager.stop()
            self.state_manager.mark_stopped()

            self.log("Farm Loop gagal dimulai.")

        else:

            self.log("Farm Loop berhasil dimulai.")

        self.refresh_status()

    def pause_bot(self):
        if self.state_manager.status != BotStatus.RUNNING:
            self.log("Bot tidak sedang berjalan.")
            return

        result = self.controller.pause_farm()

        if result:
            self.state_manager.pause()
            self.log("Bot berhasil dijeda.")
        else:
            self.log("Bot gagal dijeda.")

        self.refresh_status()

    def resume_bot(self):
        if self.state_manager.status != BotStatus.PAUSED:
            self.log("Bot tidak sedang dalam kondisi Pause.")
            return

        result = self.controller.resume_farm()

        if result:
            self.state_manager.resume()
            self.log("Bot berhasil dilanjutkan.")
        else:
            self.log("Bot gagal dilanjutkan.")

        self.refresh_status()

    def stop_bot(self):
        result = self.controller.stop_farm()

        self.state_manager.stop()
        self.state_manager.mark_stopped()

        if result:
            self.log("Bot berhasil dihentikan.")
        else:
            self.log("Perintah penghentian telah diproses.")

        self.refresh_status()

    def update_dashboard_status(self):
        current_status = self.state_manager.status

        if (
            current_status in (
                BotStatus.RUNNING,
                BotStatus.PAUSED
            )
            and not self.controller.get_farm_status()
        ):

            self.state_manager.stop()
            self.state_manager.mark_stopped()

            self.log(
                "Farm Loop selesai atau telah berhenti."
            )

        self.refresh_status()

        self.after(
            500,
            self.update_dashboard_status
        )
    # FEATURE CONTROL

    def toggle_feature(self, name):
        enabled = self.feature_vars[name].get()

        self.log(
            f"{name}: {'ON' if enabled else 'OFF'}"
        )

        if name == "Auto Reconnect":
            self.config_data["reconnect"]["enabled"] = enabled
            save_config(self.config_data)

            if enabled:
                result = self.controller.start_reconnect_monitor()

                if not result:
                    self.log(
                        "Reconnect tidak dapat dimulai. "
                        "Periksa template gambar."
                    )
            else:
                self.controller.stop_reconnect_monitor()

    def on_farm_settings_saved(self, config):

        self.config_data = config

        save_config(self.config_data)

        self.log("Pengaturan Farm berhasil disimpan.")

    def on_vision_settings_saved(self, config):

        self.config_data = config

        save_config(self.config_data)

        if self.controller.get_farm_status():
            self.log(
                "Pengaturan Vision disimpan. Hentikan Farm Loop "
                "sebelum menerapkan perubahan."
            )
            return

        result = self.controller.apply_config(
            self.config_data
        )

        if result:
            self.log("Pengaturan Vision berhasil diterapkan.")
        else:
            self.log(
                "Pengaturan Vision disimpan, tetapi belum berhasil diterapkan."
            )

    def on_reconnect_settings_saved(self, config):

        self.config_data = config

        save_config(self.config_data)

        if self.controller.get_farm_status():
            self.log(
                "Pengaturan Reconnect disimpan. Hentikan Farm Loop "
                "sebelum menerapkan perubahan."
            )
            return

        result = self.controller.apply_config(
            self.config_data
        )

        if result:
            self.log("Pengaturan Reconnect berhasil diterapkan.")
        else:
            self.log(
                "Pengaturan Reconnect disimpan, tetapi belum berhasil diterapkan."
            )

    # NAVIGATION

    def navigate(self, page):

        if page == "Dashboard":

            self.log("Dashboard aktif.")

        elif page == "Farm Settings":

            if (
                hasattr(self, "farm_settings_window")
                and self.farm_settings_window.winfo_exists()
            ):
                self.farm_settings_window.lift()
                return

            self.farm_settings_window = FarmSettingsWindow(
                self,
                self.config_data,
                self.on_farm_settings_saved
            )

        elif page == "Vision Settings":

            if (
                hasattr(self, "vision_settings_window")
                and self.vision_settings_window.winfo_exists()
            ):
                self.vision_settings_window.lift()
                return

            self.vision_settings_window = VisionSettingsWindow(
                self,
                self.config_data,
                self.on_vision_settings_saved
            )

        elif page == "Reconnect Settings":

            if (
                hasattr(self, "reconnect_settings_window")
                and self.reconnect_settings_window.winfo_exists()
            ):
                self.reconnect_settings_window.lift()
                return

            self.reconnect_settings_window = ReconnectSettingsWindow(
                self,
                self.config_data,
                self.on_reconnect_settings_saved
            )

        elif page == "Activity Logs":

            if (
                hasattr(self, "activity_logs_window")
                and self.activity_logs_window.winfo_exists()
            ):
                self.activity_logs_window.lift()
                self.activity_logs_window.refresh_logs()
                return

            self.activity_logs_window = ActivityLogsWindow(
                self
            )

        elif page == "Vision Testing":

            if (
                hasattr(self, "vision_testing_window")
                and self.vision_testing_window.winfo_exists()
            ):
                self.vision_testing_window.lift()
                return

            self.vision_testing_window = VisionTestingWindow(
                self,
                self.controller,
                self.config_data
            )

        elif page == "About":

            messagebox.showinfo(
                APP_NAME,
                f"{APP_NAME}\nVersion {APP_VERSION}"
            )

        else:

            messagebox.showinfo(
                page,
                f"Halaman {page} belum tersedia."
            )

    def on_close(self):
        try:
            self.controller.close()
        except Exception as error:
            self.log(f"Kesalahan saat menutup aplikasi: {error}")
        finally:
            self.destroy()


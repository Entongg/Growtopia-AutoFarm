
import copy
import os
import customtkinter as ctk
from tkinter import messagebox

from core.vision import Vision


DEFAULT_VISION_CONFIG = {
    "monitor_index": 1,
    "threshold": 0.85,
    "connected_template": "assets/templates/connected.png",
    "disconnected_template": "assets/templates/disconnected.png"
}


def ensure_vision_config(config):
    """Memastikan konfigurasi Vision memiliki nilai default."""

    if not isinstance(config.get("vision"), dict):
        config["vision"] = {}

    vision = config["vision"]

    for key, value in DEFAULT_VISION_CONFIG.items():
        if key not in vision:
            vision[key] = copy.deepcopy(value)

    return config


class VisionSettingsWindow(ctk.CTkToplevel):

    def __init__(self, master, config_data, on_save):

        super().__init__(master)

        self.title("Vision Settings - Growtopia AutoFarm")
        self.geometry("650x620")
        self.minsize(550, 550)
        self.configure(fg_color="#0B1424")

        self.config_data = ensure_vision_config(
            copy.deepcopy(config_data)
        )

        self.vision_config = self.config_data["vision"]
        self.on_save = on_save

        self.create_layout()

        self.transient(master)
        self.focus()

    def create_layout(self):

        main = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent"
        )

        main.pack(
            fill="both",
            expand=True,
            padx=24,
            pady=20
        )

        ctk.CTkLabel(
            main,
            text="Vision Settings",
            font=("Arial", 27, "bold"),
            text_color="#F1F5F9"
        ).pack(anchor="w")

        ctk.CTkLabel(
            main,
            text="Atur monitor, tingkat deteksi, dan template gambar.",
            text_color="#94A3B8"
        ).pack(anchor="w", pady=(4, 20))

        # MONITOR SETTINGS

        monitor_frame = self.create_section(
            main,
            "Monitor Settings"
        )

        ctk.CTkLabel(
            monitor_frame,
            text="Monitor yang digunakan",
            text_color="#CBD5E1"
        ).pack(anchor="w", padx=14, pady=(12, 5))

        self.monitor_menu = ctk.CTkOptionMenu(
            monitor_frame,
            values=["1"],
            width=200
        )

        self.monitor_menu.pack(
            anchor="w",
            padx=14,
            pady=(0, 14)
        )

        self.load_monitors()

        # DETECTION SETTINGS

        detection_frame = self.create_section(
            main,
            "Detection Settings"
        )

        ctk.CTkLabel(
            detection_frame,
            text="Confidence Threshold (0.50 - 1.00)",
            text_color="#CBD5E1"
        ).pack(anchor="w", padx=14, pady=(12, 5))

        self.threshold_entry = ctk.CTkEntry(
            detection_frame,
            width=200,
            fg_color="#0C1728"
        )

        self.threshold_entry.pack(
            anchor="w",
            padx=14,
            pady=(0, 14)
        )

        self.threshold_entry.insert(
            0,
            str(self.vision_config["threshold"])
        )

        # TEMPLATE SETTINGS

        template_frame = self.create_section(
            main,
            "Template Settings"
        )

        self.connected_entry = self.add_path_entry(
            template_frame,
            "Template Connected",
            self.vision_config["connected_template"]
        )

        self.disconnected_entry = self.add_path_entry(
            template_frame,
            "Template Disconnected",
            self.vision_config["disconnected_template"]
        )

        # TEMPLATE STATUS

        self.status_label = ctk.CTkLabel(
            main,
            text="",
            text_color="#94A3B8",
            justify="left"
        )

        self.status_label.pack(
            anchor="w",
            pady=10
        )

        self.refresh_template_status()

        # BUTTONS

        button_frame = ctk.CTkFrame(
            main,
            fg_color="transparent"
        )

        button_frame.pack(
            fill="x",
            pady=20
        )

        ctk.CTkButton(
            button_frame,
            text="Reset Settings",
            fg_color="#475569",
            hover_color="#334155",
            command=self.reset_settings
        ).pack(
            side="left",
            expand=True,
            fill="x",
            padx=(0, 6)
        )

        ctk.CTkButton(
            button_frame,
            text="Save Settings",
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self.save_settings
        ).pack(
            side="left",
            expand=True,
            fill="x",
            padx=(6, 0)
        )

    def create_section(self, parent, title):

        frame = ctk.CTkFrame(
            parent,
            fg_color="#142238",
            corner_radius=12
        )

        frame.pack(
            fill="x",
            pady=9
        )

        ctk.CTkLabel(
            frame,
            text=title,
            font=("Arial", 16, "bold"),
            text_color="#60A5FA"
        ).pack(
            anchor="w",
            padx=14,
            pady=(14, 5)
        )

        return frame

    def add_path_entry(self, parent, label, value):

        ctk.CTkLabel(
            parent,
            text=label,
            text_color="#CBD5E1"
        ).pack(
            anchor="w",
            padx=14,
            pady=(10, 4)
        )

        entry = ctk.CTkEntry(
            parent,
            height=35,
            fg_color="#0C1728",
            border_color="#334155"
        )

        entry.pack(
            fill="x",
            padx=14,
            pady=(0, 8)
        )

        entry.insert(0, str(value))

        return entry

    def load_monitors(self):

        try:
            vision = Vision()

            monitor_count = len(vision.sct.monitors) - 1

            vision.close()

            if monitor_count < 1:
                monitor_count = 1

            monitor_values = [
                str(index)
                for index in range(1, monitor_count + 1)
            ]

            self.monitor_menu.configure(
                values=monitor_values
            )

            current_monitor = str(
                self.vision_config["monitor_index"]
            )

            if current_monitor not in monitor_values:
                current_monitor = "1"

            self.monitor_menu.set(current_monitor)

        except Exception as error:

            self.monitor_menu.configure(
                values=["1"]
            )

            self.monitor_menu.set("1")

            self.status_label_text = (
                f"Monitor tidak dapat diperiksa: {error}"
            )

    def refresh_template_status(self):

        connected_path = self.connected_entry.get().strip()
        disconnected_path = self.disconnected_entry.get().strip()

        connected_exists = os.path.isfile(connected_path)
        disconnected_exists = os.path.isfile(disconnected_path)

        connected_status = (
            "Tersedia" if connected_exists else "Belum ditemukan"
        )

        disconnected_status = (
            "Tersedia" if disconnected_exists else "Belum ditemukan"
        )

        self.status_label.configure(
            text=(
                f"Connected template: {connected_status}\n"
                f"Disconnected template: {disconnected_status}"
            )
        )

    def reset_settings(self):

        self.monitor_menu.set(
            str(DEFAULT_VISION_CONFIG["monitor_index"])
        )

        self.threshold_entry.delete(0, "end")
        self.threshold_entry.insert(
            0,
            str(DEFAULT_VISION_CONFIG["threshold"])
        )

        self.connected_entry.delete(0, "end")
        self.connected_entry.insert(
            0,
            DEFAULT_VISION_CONFIG["connected_template"]
        )

        self.disconnected_entry.delete(0, "end")
        self.disconnected_entry.insert(
            0,
            DEFAULT_VISION_CONFIG["disconnected_template"]
        )

        self.refresh_template_status()

    def save_settings(self):

        try:

            monitor_index = int(
                self.monitor_menu.get()
            )

            threshold = float(
                self.threshold_entry.get().strip()
            )

            connected_template = (
                self.connected_entry.get().strip()
            )

            disconnected_template = (
                self.disconnected_entry.get().strip()
            )

            if monitor_index < 1:
                raise ValueError(
                    "Monitor index minimal 1."
                )

            if not 0.50 <= threshold <= 1.00:
                raise ValueError(
                    "Threshold harus berada antara 0.50 sampai 1.00."
                )

            if not connected_template:
                raise ValueError(
                    "Path connected template tidak boleh kosong."
                )

            if not disconnected_template:
                raise ValueError(
                    "Path disconnected template tidak boleh kosong."
                )

            # Validasi monitor berdasarkan jumlah monitor aktual.
            vision = Vision(
                monitor_index=monitor_index
            )
            vision.close()

            self.config_data["vision"] = {
                "monitor_index": monitor_index,
                "threshold": threshold,
                "connected_template": connected_template,
                "disconnected_template": disconnected_template
            }

            self.on_save(self.config_data)

            messagebox.showinfo(
                "Berhasil",
                "Pengaturan Vision berhasil disimpan.",
                parent=self
            )

            self.destroy()

        except ValueError as error:

            messagebox.showerror(
                "Pengaturan Tidak Valid",
                str(error),
                parent=self
            )

        except Exception as error:

            messagebox.showerror(
                "Gagal Menyimpan",
                str(error),
                parent=self
            )

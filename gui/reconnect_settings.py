
import copy
import customtkinter as ctk
from tkinter import messagebox


DEFAULT_RECONNECT_CONFIG = {
    "enabled": False,
    "interval": 2.0,
    "confirm_count": 2
}


def ensure_reconnect_config(config):

    if not isinstance(config.get("reconnect"), dict):
        config["reconnect"] = {}

    reconnect = config["reconnect"]

    for key, value in DEFAULT_RECONNECT_CONFIG.items():
        if key not in reconnect:
            reconnect[key] = copy.deepcopy(value)

    return config


class ReconnectSettingsWindow(ctk.CTkToplevel):

    def __init__(self, master, config_data, on_save):

        super().__init__(master)

        self.title("Reconnect Settings - Growtopia AutoFarm")
        self.geometry("600x570")
        self.minsize(500, 500)
        self.configure(fg_color="#0B1424")

        self.config_data = ensure_reconnect_config(
            copy.deepcopy(config_data)
        )

        self.reconnect_config = self.config_data["reconnect"]
        self.on_save = on_save

        self.create_layout()

        self.transient(master)
        self.focus()

    def create_layout(self):

        main = ctk.CTkFrame(
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
            text="Reconnect Settings",
            font=("Arial", 27, "bold"),
            text_color="#F1F5F9"
        ).pack(anchor="w")

        ctk.CTkLabel(
            main,
            text="Atur pemantauan status koneksi game.",
            text_color="#94A3B8"
        ).pack(anchor="w", pady=(4, 20))

        # ENABLE RECONNECT

        enable_frame = self.create_section(
            main,
            "Monitoring Settings"
        )

        self.enabled_var = ctk.BooleanVar(
            value=self.reconnect_config["enabled"]
        )

        ctk.CTkCheckBox(
            enable_frame,
            text="Aktifkan Auto Reconnect Monitoring",
            variable=self.enabled_var,
            text_color="#CBD5E1",
            onvalue=True,
            offvalue=False
        ).pack(
            anchor="w",
            padx=14,
            pady=14
        )

        # INTERVAL

        self.interval_entry = self.add_entry(
            main,
            "Interval pemeriksaan (detik)",
            self.reconnect_config["interval"]
        )

        # CONFIRM COUNT

        self.confirm_entry = self.add_entry(
            main,
            "Jumlah deteksi konfirmasi",
            self.reconnect_config["confirm_count"]
        )

        ctk.CTkLabel(
            main,
            text=(
                "Contoh: interval 2 detik dan konfirmasi 2 kali "
                "berarti status perlu terdeteksi secara konsisten "
                "dalam dua pemeriksaan."
            ),
            text_color="#94A3B8",
            wraplength=500,
            justify="left"
        ).pack(
            anchor="w",
            pady=(12, 20)
        )

        # BUTTONS

        button_frame = ctk.CTkFrame(
            main,
            fg_color="transparent"
        )

        button_frame.pack(
            fill="x",
            side="bottom",
            pady=10
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

    def add_entry(self, parent, label, value):

        ctk.CTkLabel(
            parent,
            text=label,
            text_color="#CBD5E1"
        ).pack(
            anchor="w",
            pady=(8, 4)
        )

        entry = ctk.CTkEntry(
            parent,
            height=35,
            fg_color="#0C1728",
            border_color="#334155"
        )

        entry.pack(
            fill="x"
        )

        entry.insert(0, str(value))

        return entry

    def reset_settings(self):

        self.enabled_var.set(
            DEFAULT_RECONNECT_CONFIG["enabled"]
        )

        self.interval_entry.delete(0, "end")
        self.interval_entry.insert(
            0,
            str(DEFAULT_RECONNECT_CONFIG["interval"])
        )

        self.confirm_entry.delete(0, "end")
        self.confirm_entry.insert(
            0,
            str(DEFAULT_RECONNECT_CONFIG["confirm_count"])
        )

    def save_settings(self):

        try:

            enabled = self.enabled_var.get()

            interval = float(
                self.interval_entry.get().strip()
            )

            confirm_count = int(
                self.confirm_entry.get().strip()
            )

            if interval < 0.5:
                raise ValueError(
                    "Interval pemeriksaan minimal 0.5 detik."
                )

            if confirm_count < 1:
                raise ValueError(
                    "Jumlah konfirmasi minimal 1."
                )

            self.config_data["reconnect"] = {
                "enabled": enabled,
                "interval": interval,
                "confirm_count": confirm_count
            }

            self.on_save(self.config_data)

            messagebox.showinfo(
                "Berhasil",
                "Pengaturan Reconnect berhasil disimpan.",
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

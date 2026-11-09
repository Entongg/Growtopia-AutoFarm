
import copy
import customtkinter as ctk
from tkinter import messagebox


DEFAULT_FARM_CONFIG = {
    "auto_punch": {
        "x": 500,
        "y": 300,
        "interval": 0.5,
        "max_duration": 5,
        "max_actions": 5
    },
    "auto_put": {
        "positions": [
            [500, 300],
            [550, 300],
            [600, 300]
        ],
        "interval": 0.5,
        "button": "right",
        "max_duration": 5,
        "max_actions": 5
    },
    "cycles": 2
}


def ensure_farm_config(config):
    """Memastikan konfigurasi farming memiliki nilai default."""

    if not isinstance(config.get("farm"), dict):
        config["farm"] = {}

    farm = config["farm"]

    for key, value in DEFAULT_FARM_CONFIG.items():
        if key not in farm:
            farm[key] = copy.deepcopy(value)

    for section in ("auto_punch", "auto_put"):
        if not isinstance(farm.get(section), dict):
            farm[section] = {}

        for key, value in DEFAULT_FARM_CONFIG[section].items():
            if key not in farm[section]:
                farm[section][key] = copy.deepcopy(value)

    return config


class FarmSettingsWindow(ctk.CTkToplevel):

    def __init__(self, master, config_data, on_save):

        super().__init__(master)

        self.title("Farm Settings - Growtopia AutoFarm")
        self.geometry("700x760")
        self.minsize(600, 650)
        self.configure(fg_color="#0B1424")

        self.config_data = ensure_farm_config(
            copy.deepcopy(config_data)
        )

        self.on_save = on_save

        self.farm_config = self.config_data["farm"]

        self.punch_config = self.farm_config["auto_punch"]
        self.put_config = self.farm_config["auto_put"]

        self.entries = {}

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
            text="Farm Settings",
            font=("Arial", 27, "bold"),
            text_color="#F1F5F9"
        ).pack(anchor="w")

        ctk.CTkLabel(
            main,
            text="Atur konfigurasi Auto Punch, Auto Put, dan Farm Loop.",
            text_color="#94A3B8"
        ).pack(anchor="w", pady=(4, 20))

        # AUTO PUNCH

        punch_frame = self.create_section(
            main,
            "Auto Punch Settings"
        )

        self.add_entry(
            punch_frame,
            "punch_x",
            "Koordinat X",
            self.punch_config["x"]
        )

        self.add_entry(
            punch_frame,
            "punch_y",
            "Koordinat Y",
            self.punch_config["y"]
        )

        self.add_entry(
            punch_frame,
            "punch_interval",
            "Interval (detik)",
            self.punch_config["interval"]
        )

        self.add_entry(
            punch_frame,
            "punch_duration",
            "Maksimal durasi (detik)",
            self.punch_config["max_duration"]
        )

        self.add_entry(
            punch_frame,
            "punch_actions",
            "Maksimal jumlah aksi",
            self.punch_config["max_actions"]
        )

        # AUTO PUT

        put_frame = self.create_section(
            main,
            "Auto Put Settings"
        )

        ctk.CTkLabel(
            put_frame,
            text="Daftar koordinat (format X,Y per baris)",
            text_color="#CBD5E1"
        ).pack(anchor="w", padx=14, pady=(12, 5))

        self.positions_box = ctk.CTkTextbox(
            put_frame,
            height=110,
            fg_color="#0C1728"
        )

        self.positions_box.pack(
            fill="x",
            padx=14,
            pady=(0, 12)
        )

        positions_text = "\n".join(
            f"{position[0]},{position[1]}"
            for position in self.put_config["positions"]
        )

        self.positions_box.insert(
            "1.0",
            positions_text
        )

        self.add_entry(
            put_frame,
            "put_interval",
            "Interval (detik)",
            self.put_config["interval"]
        )

        self.add_entry(
            put_frame,
            "put_duration",
            "Maksimal durasi (detik)",
            self.put_config["max_duration"]
        )

        self.add_entry(
            put_frame,
            "put_actions",
            "Maksimal jumlah aksi",
            self.put_config["max_actions"]
        )

        ctk.CTkLabel(
            put_frame,
            text="Tombol mouse",
            text_color="#CBD5E1"
        ).pack(anchor="w", padx=14, pady=(10, 4))

        self.mouse_button = ctk.CTkOptionMenu(
            put_frame,
            values=["left", "right"]
        )

        self.mouse_button.pack(
            anchor="w",
            padx=14,
            pady=(0, 14)
        )

        self.mouse_button.set(
            self.put_config["button"]
        )

        # FARM LOOP

        loop_frame = self.create_section(
            main,
            "Farm Loop Settings"
        )

        self.add_entry(
            loop_frame,
            "cycles",
            "Jumlah siklus farming",
            self.farm_config["cycles"]
        )

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

    def add_entry(self, parent, key, label, value):

        ctk.CTkLabel(
            parent,
            text=label,
            text_color="#CBD5E1"
        ).pack(
            anchor="w",
            padx=14,
            pady=(8, 4)
        )

        entry = ctk.CTkEntry(
            parent,
            height=35,
            fg_color="#0C1728",
            border_color="#334155"
        )

        entry.pack(
            fill="x",
            padx=14
        )

        entry.insert(0, str(value))

        self.entries[key] = entry

    def get_number(self, key, label, integer=False, minimum=0):

        raw_value = self.entries[key].get().strip()

        try:
            value = int(raw_value) if integer else float(raw_value)

        except ValueError:
            raise ValueError(
                f"{label} harus berupa angka yang valid."
            )

        if value < minimum:
            raise ValueError(
                f"{label} minimal {minimum}."
            )

        return value

    def parse_positions(self):

        raw_text = self.positions_box.get(
            "1.0",
            "end"
        ).strip()

        if not raw_text:
            raise ValueError(
                "Daftar koordinat Auto Put tidak boleh kosong."
            )

        positions = []

        for line_number, line in enumerate(
            raw_text.splitlines(),
            start=1
        ):

            try:
                parts = line.split(",")

                if len(parts) != 2:
                    raise ValueError

                x = int(parts[0].strip())
                y = int(parts[1].strip())

                if x < 0 or y < 0:
                    raise ValueError

                positions.append([x, y])

            except ValueError:
                raise ValueError(
                    f"Koordinat pada baris {line_number} "
                    "tidak valid. Gunakan format X,Y."
                )

        return positions

    def collect_settings(self):

        punch = {
            "x": self.get_number(
                "punch_x", "Koordinat X", True
            ),
            "y": self.get_number(
                "punch_y", "Koordinat Y", True
            ),
            "interval": self.get_number(
                "punch_interval", "Interval Punch", minimum=0.05
            ),
            "max_duration": self.get_number(
                "punch_duration", "Durasi Punch", minimum=0.1
            ),
            "max_actions": self.get_number(
                "punch_actions", "Jumlah aksi Punch", True, 1
            )
        }

        put = {
            "positions": self.parse_positions(),
            "interval": self.get_number(
                "put_interval", "Interval Put", minimum=0.05
            ),
            "button": self.mouse_button.get(),
            "max_duration": self.get_number(
                "put_duration", "Durasi Put", minimum=0.1
            ),
            "max_actions": self.get_number(
                "put_actions", "Jumlah aksi Put", True, 1
            )
        }

        cycles = self.get_number(
            "cycles", "Jumlah siklus", True, 1
        )

        return {
            "auto_punch": punch,
            "auto_put": put,
            "cycles": cycles
        }

    def save_settings(self):

        try:
            new_farm_config = self.collect_settings()

            self.config_data["farm"] = new_farm_config

            self.on_save(self.config_data)

            messagebox.showinfo(
                "Berhasil",
                "Pengaturan Farm berhasil disimpan.",
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

    def reset_settings(self):

        self.punch_config = copy.deepcopy(
            DEFAULT_FARM_CONFIG["auto_punch"]
        )

        self.put_config = copy.deepcopy(
            DEFAULT_FARM_CONFIG["auto_put"]
        )

        self.farm_config = copy.deepcopy(
            DEFAULT_FARM_CONFIG
        )

        for key, value in {
            "punch_x": 500,
            "punch_y": 300,
            "punch_interval": 0.5,
            "punch_duration": 5,
            "punch_actions": 5,
            "put_interval": 0.5,
            "put_duration": 5,
            "put_actions": 5,
            "cycles": 2
        }.items():

            self.entries[key].delete(0, "end")
            self.entries[key].insert(0, str(value))

        self.positions_box.delete("1.0", "end")
        self.positions_box.insert(
            "1.0",
            "500,300\n550,300\n600,300"
        )

        self.mouse_button.set("right")

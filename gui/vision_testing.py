
import customtkinter as ctk
from tkinter import messagebox


class VisionTestingWindow(ctk.CTkToplevel):

    def __init__(self, master, controller, config_data):

        super().__init__(master)

        self.controller = controller
        self.config_data = config_data

        self.title("Vision Testing - Growtopia AutoFarm")
        self.geometry("650x520")
        self.minsize(550, 450)
        self.configure(fg_color="#0B1424")

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
            pady=22
        )

        ctk.CTkLabel(
            main,
            text="Vision Testing",
            font=("Arial", 27, "bold"),
            text_color="#F1F5F9"
        ).pack(anchor="w")

        ctk.CTkLabel(
            main,
            text="Uji pendeteksian template pada layar.",
            text_color="#94A3B8"
        ).pack(anchor="w", pady=(4, 22))

        # TEMPLATE SELECTOR

        ctk.CTkLabel(
            main,
            text="Pilih template",
            text_color="#CBD5E1"
        ).pack(anchor="w", pady=(0, 6))

        self.template_menu = ctk.CTkOptionMenu(
            main,
            values=["Connected", "Disconnected"],
            width=220
        )

        self.template_menu.pack(anchor="w")
        self.template_menu.set("Connected")

        # THRESHOLD INFORMATION

        threshold = self.config_data.get(
            "vision", {}
        ).get("threshold", 0.85)

        self.threshold_label = ctk.CTkLabel(
            main,
            text=f"Threshold aktif: {threshold:.2f}",
            text_color="#94A3B8"
        )

        self.threshold_label.pack(
            anchor="w",
            pady=(14, 18)
        )

        # TEST BUTTON

        ctk.CTkButton(
            main,
            text="Test Detection",
            height=42,
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self.run_test
        ).pack(
            fill="x",
            pady=(0, 18)
        )

        # RESULT FRAME

        result_frame = ctk.CTkFrame(
            main,
            fg_color="#142238",
            corner_radius=12
        )

        result_frame.pack(
            fill="both",
            expand=True
        )

        ctk.CTkLabel(
            result_frame,
            text="Detection Result",
            font=("Arial", 17, "bold"),
            text_color="#60A5FA"
        ).pack(
            anchor="w",
            padx=16,
            pady=(16, 12)
        )

        self.result_label = ctk.CTkLabel(
            result_frame,
            text="Belum ada pengujian.",
            font=("Arial", 14),
            text_color="#CBD5E1",
            justify="left",
            anchor="nw"
        )

        self.result_label.pack(
            fill="both",
            expand=True,
            padx=16,
            pady=(0, 16)
        )

    def run_test(self):

        template_name = self.template_menu.get()

        self.result_label.configure(
            text="Sedang mengambil screenshot dan melakukan deteksi...",
            text_color="#FBBF24"
        )

        self.update_idletasks()

        try:

            result = self.controller.test_template(
                template_name
            )

            confidence = result["confidence"]
            threshold = result["threshold"]

            if result["found"]:
                status = "TEMPLATE TERDETEKSI"
                status_color = "#22C55E"
            else:
                status = "TEMPLATE TIDAK MEMENUHI THRESHOLD"
                status_color = "#F59E0B"

            result_text = (
                f"Template: {template_name}\n"
                f"Status: {status}\n\n"
                f"Confidence: {confidence:.4f}\n"
                f"Threshold: {threshold:.2f}\n\n"
                f"Posisi tengah template:\n"
                f"X: {result['x']}\n"
                f"Y: {result['y']}\n\n"
                f"Ukuran template:\n"
                f"Width: {result['width']}\n"
                f"Height: {result['height']}"
            )

            self.result_label.configure(
                text=result_text,
                text_color=status_color
            )

        except Exception as error:

            self.result_label.configure(
                text=f"Pengujian gagal:\n{error}",
                text_color="#F87171"
            )

            messagebox.showerror(
                "Vision Testing Error",
                str(error),
                parent=self
            )

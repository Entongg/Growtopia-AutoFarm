
import customtkinter as ctk

from config import LOG_DIR


class ActivityLogsWindow(ctk.CTkToplevel):

    def __init__(self, master):

        super().__init__(master)

        self.title("Activity Logs - Growtopia AutoFarm")
        self.geometry("850x600")
        self.minsize(650, 450)
        self.configure(fg_color="#0B1424")

        self.log_path = LOG_DIR / "app.log"

        self.create_layout()
        self.refresh_logs()

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
            padx=22,
            pady=20
        )

        header = ctk.CTkFrame(
            main,
            fg_color="transparent"
        )

        header.pack(fill="x")

        ctk.CTkLabel(
            header,
            text="Activity Logs",
            font=("Arial", 27, "bold"),
            text_color="#F1F5F9"
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="Refresh",
            width=110,
            command=self.refresh_logs
        ).pack(side="right")

        ctk.CTkLabel(
            main,
            text=f"Log file: {self.log_path}",
            text_color="#94A3B8"
        ).pack(
            anchor="w",
            pady=(6, 14)
        )

        self.log_box = ctk.CTkTextbox(
            main,
            fg_color="#0C1728",
            text_color="#CBD5E1",
            font=("Consolas", 12),
            wrap="none"
        )

        self.log_box.pack(
            fill="both",
            expand=True
        )

        self.log_box.configure(
            state="disabled"
        )

        self.status_label = ctk.CTkLabel(
            main,
            text="",
            text_color="#94A3B8"
        )

        self.status_label.pack(
            anchor="w",
            pady=(10, 0)
        )

    def refresh_logs(self):

        try:

            if not self.log_path.exists():

                content = (
                    "Belum ada file log.\n"
                    "Jalankan aplikasi untuk menghasilkan log."
                )

                total_lines = 0

            else:

                with open(
                    self.log_path,
                    "r",
                    encoding="utf-8",
                    errors="replace"
                ) as file:

                    lines = file.readlines()

                total_lines = len(lines)

                content = "".join(
                    lines[-1000:]
                )

                if not content:
                    content = "File log masih kosong."

            self.log_box.configure(
                state="normal"
            )

            self.log_box.delete(
                "1.0",
                "end"
            )

            self.log_box.insert(
                "1.0",
                content
            )

            self.log_box.see("end")

            self.log_box.configure(
                state="disabled"
            )

            self.status_label.configure(
                text=(
                    f"Total baris: {total_lines} | "
                    f"Ditampilkan: {min(total_lines, 1000)}"
                )
            )

        except OSError as error:

            self.status_label.configure(
                text=f"Gagal membaca log: {error}",
                text_color="#F87171"
            )

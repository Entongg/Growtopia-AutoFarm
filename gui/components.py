
import customtkinter as ctk


class MetricCard(ctk.CTkFrame):

    def __init__(
        self,
        master,
        title,
        value,
        accent="#3B82F6"
    ):

        super().__init__(
            master,
            corner_radius=14,
            fg_color="#17243A"
        )

        ctk.CTkLabel(
            self,
            text=title,
            text_color="#9AAAC1",
            font=("Arial", 12, "bold")
        ).pack(
            anchor="w",
            padx=16,
            pady=(14, 4)
        )

        self.value_label = ctk.CTkLabel(
            self,
            text=value,
            text_color=accent,
            font=("Arial", 24, "bold")
        )

        self.value_label.pack(
            anchor="w",
            padx=16,
            pady=(0, 14)
        )

    def set_value(self, value):

        self.value_label.configure(
            text=str(value)
        )

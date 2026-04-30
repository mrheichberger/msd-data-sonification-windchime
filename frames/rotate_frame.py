import customtkinter as ctk


class RotateFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        # =========================
        # GRID CONFIG (UNIFORM 4x2)
        # =========================
        self.grid_rowconfigure(0, weight=0)  # Title row

        # 4 rows for buttons
        for row in range(1, 5):
            self.grid_rowconfigure(row, weight=1, uniform="row")

        # 2 equal columns
        for col in range(2):
            self.grid_columnconfigure(col, weight=1, uniform="col")

        # =========================
        # TITLE
        # =========================
        ctk.CTkLabel(
            self,
            text="Rotate Chimes",
            font=("Helvetica", 24, "bold")
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            pady=20
        )

        # =========================
        # BUTTON STYLE
        # =========================
        button_style = {
            "corner_radius": 10,
            "font": ("Helvetica", 16),
            "fg_color": "#F76902",
            "hover_color": "#BB4E00",
            "text_color": "#FFFFFF"
        }

        # =========================
        # 8 CHIME BUTTONS (4x2)
        # =========================
        for i in range(8):
            row = (i // 2) + 1   # Rows 1-4
            col = i % 2          # Columns 0-1

            ctk.CTkButton(
                self,
                text=f"Rotate Chime {i + 1}",
                command=lambda idx=i: self.rotate_chime(idx),
                **button_style
            ).grid(
                row=row,
                column=col,
                padx=10,
                pady=10,
                sticky="nsew"
            )


        # =========================
        # BACK BUTTON
        # =========================
        self.back_button = ctk.CTkButton(
            self,
            text="Back",
            command=lambda: controller.show_frame("HomeFrame"),
            **button_style
        )
        self.back_button.grid(row=5, column=0, padx=10, pady=10, columnspan=2, sticky="nesw")

    # =========================
    # ROTATE FUNCTION
    # =========================
    def rotate_chime(self, idx):
        print(f"Rotating Chime {idx + 1}")
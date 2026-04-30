import customtkinter as ctk


class HomeFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        # =========================
        # MAIN GRID = UNIFORM 2x2
        # =========================
        self.grid_rowconfigure(0, weight=0)  # Title row
        self.grid_rowconfigure(1, weight=1, uniform="row")
        self.grid_rowconfigure(2, weight=1, uniform="row")

        self.grid_columnconfigure(0, weight=1, uniform="col")
        self.grid_columnconfigure(1, weight=1, uniform="col")

        # =========================
        # TITLE
        # =========================
        ctk.CTkLabel(
            self,
            text="Home Page",
            font=("Helvetica", 24, "bold")
        ).grid(
            row=0,
            column=0,
            columnspan=2,
            pady=10
        )

        # =========================
        # BUTTON STYLE
        # =========================
        self.button_style = {
            "corner_radius": 10,
            "font": ("Helvetica", 16),
            "fg_color": "#F76902",
            "hover_color": "#BB4E00",
            "text_color": "#FFFFFF",
            "anchor": "center"
        }

        # Initial UI
        self.update_mode_ui()

    # =========================
    # REFRESH WHEN PAGE OPENS
    # =========================
    def on_show(self):
        self.update_mode_ui()

    # =========================
    # MODE UI
    # =========================
    def update_mode_ui(self):

        # Remove old buttons (keep title)
        for widget in self.winfo_children():
            info = widget.grid_info()
            if info and int(info["row"]) > 0:
                widget.destroy()

        mode = self.controller.current_mode

        # =========================
        # WEATHER MODE
        # =========================
        if mode == "Weather Mode":

            # Top Left
            ctk.CTkButton(
                self,
                text="Change Mode",
                command=lambda: self.controller.show_frame("ModeSelectionFrame"),
                **self.button_style
            ).grid(
                row=1,
                column=0,
                padx=10,
                pady=10,
                sticky="nsew"
            )

            # Bottom left
            ctk.CTkButton(
                self,
                text="Monitor Data",
                command=lambda: self.controller.show_frame("MonitorFrame"),
                **self.button_style
            ).grid(
                row=2,
                column=0,
                padx=10,
                pady=10,
                sticky="nsew"
            )

            # Top Right
            ctk.CTkButton(
                self,
                text="Weather Mood Configurations",
                command=lambda: self.controller.show_frame("WeatherMoodFrame"),
                **self.button_style
            ).grid(
                row=1,
                column=1,
                padx=10,
                pady=10,
                sticky="nsew"
            )

            # Bottom Right
            ctk.CTkButton(
                self,
                text=f"Current Mode:\n{mode}",
                **self.button_style
            ).grid(
                row=2,
                column=1,
                padx=10,
                pady=10,
                sticky="nsew"
            )

        # =========================
        # USER MODE
        # =========================
        else:

            # Top Left
            ctk.CTkButton(
                self,
                text="Change Mode",
                command=lambda: self.controller.show_frame("ModeSelectionFrame"),
                **self.button_style
            ).grid(
                row=1,
                column=0,
                padx=10,
                pady=10,
                sticky="nsew"
            )

            # Top Right
            ctk.CTkButton(
                self,
                text="Timetable Configurations",
                command=lambda: self.controller.show_frame("TimetableConfigFrame"),
                **self.button_style
            ).grid(
                row=1,
                column=1,
                padx=10,
                pady=10,
                sticky="nsew"
            )

            # Bottom Left
            ctk.CTkButton(
                self,
                text="Rotate Configurations",
                command=lambda: self.controller.show_frame("RotateFrame"),
                **self.button_style
            ).grid(
                row=2,
                column=0,
                padx=10,
                pady=10,
                sticky="nsew"
            )

            # Bottom Right
            ctk.CTkButton(
                self,
                text="Chime Configurations",
                command=lambda: self.controller.show_frame("ChimeConfigFrame"),
                **self.button_style
            ).grid(
                row=2,
                column=1,
                padx=10,
                pady=10,
                sticky="nsew"
            )
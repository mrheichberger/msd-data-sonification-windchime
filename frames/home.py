import customtkinter as ctk

class HomeFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1, uniform="row")
        self.grid_rowconfigure(2, weight=1, uniform="row")
        self.grid_columnconfigure(0, weight=1, uniform="col")
        self.grid_columnconfigure(1, weight=1, uniform="col")

        ctk.CTkLabel(self, text="Home Page",
                    font=("Helvetica", 24, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        button_style = {
            "corner_radius": 10,
            "font": ("Helvetica", 16),
            "fg_color": "#F76902",
            "hover_color": "#BB4E00",
            "text_color": "#FFFFFF"
        }

        ctk.CTkButton(
            self,
            text="Change Mode",
            command=lambda: controller.show_frame("ModeSelectionFrame"),
            **button_style
        ).grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        ctk.CTkButton(
            self,
            text="Monitor Data",
            command=lambda: controller.show_frame("MonitorFrame"),
            **button_style
        ).grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        self.dynamic_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.dynamic_frame.grid(row=1, column=1, rowspan=2, padx=0, pady=0, sticky="nsew")

        self.dynamic_frame.grid_rowconfigure(0, weight=1, uniform="row")
        self.dynamic_frame.grid_rowconfigure(1, weight=1, uniform="row")
        self.dynamic_frame.grid_columnconfigure(0, weight=1)
        self.dynamic_frame.grid_propagate(False)
        
        self.update_mode_ui()

    def on_show(self):
        self.update_mode_ui()

    def update_mode_ui(self):
        
        button_style = {
                "corner_radius": 10,
                "font": ("Helvetica", 16),
                "fg_color": "#F76902",
                "hover_color": "#BB4E00",
                "text_color": "#FFFFFF"
            }
        
        for widget in self.dynamic_frame.winfo_children():
            widget.destroy()

        mode = self.controller.current_mode

        if mode == "Weather Mode":

            ctk.CTkButton(
                self.dynamic_frame,
                text="Weather Mood Configurations",
                command=lambda: self.controller.show_frame("WeatherMoodFrame"),
                **button_style
            ).grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

            ctk.CTkButton(
                self.dynamic_frame,
                text=f"Current Mode: {mode}",
                **button_style
            ).grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        else:
            ctk.CTkButton(
                self.dynamic_frame,
                text="Timetable Configurations",
                command=lambda: self.controller.show_frame("TimetableConfigFrame"),
                **button_style
            ).grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

            ctk.CTkButton(
                self.dynamic_frame,
                text="Chime Configurations",
                command=lambda: self.controller.show_frame("ChimeConfigFrame"),
                **button_style
            ).grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
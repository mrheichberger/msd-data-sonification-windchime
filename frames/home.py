import customtkinter as ctk


class HomeFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
    
        title = ctk.CTkLabel(
            self,
            text="Home Page",
            font=("Helvetica", 24, "bold")
        )
        title.grid(row=0, column=0, columnspan=2, pady=10, sticky="n")

        button_style = {
            "width": 200,
            "height": 50,
            "corner_radius": 10,
            "font": ("Helvetica", 16),
            "fg_color": "#F76902",
            "hover_color": "#BB4E00",
            "text_color": "#FFFFFF"
        }
        
        change_button = ctk.CTkButton(
            self, 
            text="Change Mode",
            command=lambda: controller.show_frame("ModeSelectionFrame"),
            **button_style
        ).grid(row=1, column=0, padx =10, pady=10, sticky="nsew")

        monitor_button = ctk.CTkButton(
            self, 
            text="Monitor Data",
            command=lambda: controller.show_frame("MonitorFrame"),
            **button_style
        ).grid(row=2, column=0, padx =10, pady=10, sticky="nsew")

        timetable_button = ctk.CTkButton(
            self, 
            text="Timetable Configurations",
            command=lambda: controller.show_frame("TimetableConfigFrame"),
            **button_style
        ).grid(row=1, column=1, padx =10, pady=10, sticky="nsew")
        
        update_chime_button = ctk.CTkButton(
            self, 
            text="Chime Configurations",
            command=lambda: controller.show_frame("ChimeConfigFrame"),
            **button_style
        ).grid(row=2, column=1, padx =10, pady=10, sticky="nsew")
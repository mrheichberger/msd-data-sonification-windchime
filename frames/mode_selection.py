import customtkinter as ctk

class ModeSelectionFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        self.default_color = "#F76902"
        self.selected_color = "#BB4E00"
        
        # make THIS frame expandable
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        container = ctk.CTkFrame(self)
        container.grid(row=0, column=0)  # sits in the center because of weights

        # optional: tighten layout inside container
        container.grid_columnconfigure(0, weight=1)

        # title
        ctk.CTkLabel(
            container,
            text="Change Mode",
            font=("Helvetica", 28, "bold")
        ).grid(row=0, column=0, pady=(20, 40), columnspan=2)

        # buttons
        self.user_btn = ctk.CTkButton(
            container,
            text="User Mode",
            width=200,
            height=50,
            command=lambda: self.select_mode("User Mode")
        )
        self.user_btn.grid(row=1, column=0, pady=10)

        self.weather_btn = ctk.CTkButton(
            container,
            text="Weather Mode",
            width=200,
            height=50,
            command=lambda: self.select_mode("Weather Mode")
        )
        self.weather_btn.grid(row=1, column=1, pady=10)

        # confirm
        ctk.CTkButton(
            container,
            text="Confirm",
            width=200,
            height=50,
            command=self.confirm
        ).grid(row=2, column=0, pady=(30, 20), columnspan=2)

    def select_mode(self, mode):
        self.selected_mode = mode
        self.update_selection_ui()

    def update_selection_ui(self):
        # reset both
        self.user_btn.configure(fg_color=self.default_color)
        self.weather_btn.configure(fg_color=self.default_color)

        # highlight selected
        if self.selected_mode == "User Mode":
            self.user_btn.configure(fg_color=self.selected_color)
        elif self.selected_mode == "Weather Mode":
            self.weather_btn.configure(fg_color=self.selected_color)

    def confirm(self):
        print(f"[MODE_SELECTION] Confirming mode={self.selected_mode}")
        self.controller.set_mode(self.selected_mode)
        self.controller.show_frame("HomeFrame")
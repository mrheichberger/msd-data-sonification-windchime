import customtkinter as ctk

class ModeSelectionFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.selected_mode = controller.current_mode

        ctk.CTkLabel(self, text="Change Mode",
                     font=("Helvetica", 20, "bold")).pack(pady=20)

        ctk.CTkButton(self, text="User Mode",
                      command=lambda: self.select_mode("User Mode")).pack(pady=10)

        ctk.CTkButton(self, text="Weather Mode",
                      command=lambda: self.select_mode("Weather Mode")).pack(pady=10)

        ctk.CTkButton(self, text="Confirm",
                      command=self.confirm).pack(pady=20)

    def select_mode(self, mode):
        self.selected_mode = mode

    def confirm(self):
        self.controller.current_mode = self.selected_mode
        self.controller.show_frame("HomeFrame")
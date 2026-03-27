import customtkinter as ctk

class MonitorFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        ctk.CTkLabel(self, text="Weather Monitor",
                     font=("Helvetica", 20, "bold")).pack(pady=10)

        self.label = ctk.CTkLabel(self, text="")
        self.label.pack(pady=20)

        ctk.CTkButton(self, text="Go Home",
                      command=lambda: controller.show_frame("HomeFrame")).pack()

    def on_show(self):
        self.label.configure(text=str(self.controller.weather))
import customtkinter as ctk
import json

class TimetableConfigFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.configurations = []

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header
        header = ctk.CTkLabel(self, text="Timetable Configurations",
                              font=("Helvetica", 22, "bold"))
        header.grid(row=0, column=0, pady=10)

        self.current_label = ctk.CTkLabel(self, text="")
        self.current_label.grid(row=1, column=0)

        # Scrollable list
        self.scroll = ctk.CTkScrollableFrame(self)
        self.scroll.grid(row=2, column=0, sticky="nsew", padx=20, pady=10)

        # Buttons
        btn_frame = ctk.CTkFrame(self)
        btn_frame.grid(row=3, column=0, pady=10)

        ctk.CTkButton(btn_frame, text="Create",
                      command=self.create_configuration).pack(side="left", padx=10)

        ctk.CTkButton(btn_frame, text="Go Home",
                      command=lambda: controller.show_frame("HomeFrame")).pack(side="left", padx=10)

        self.load_configurations()
        self.refresh()

    # ----------------------------
    # File Handling
    # ----------------------------

    def load_configurations(self):
        try:
            with open("timetable_configs.json", "r") as f:
                self.configurations = json.load(f)
        except FileNotFoundError:
            self.configurations = []

    def save_configurations(self):
        with open("timetable_configs.json", "w") as f:
            json.dump(self.configurations, f, indent=4)

    # ----------------------------
    # UI Logic
    # ----------------------------

    def refresh(self):
        for widget in self.scroll.winfo_children():
            widget.destroy()

        for index, config in enumerate(self.configurations):
            frame = ctk.CTkFrame(self.scroll)
            frame.pack(fill="x", pady=5)

            ctk.CTkLabel(frame, text=config["name"],
                         font=("Helvetica", 14, "bold")).pack(side="left", padx=10)

            ctk.CTkButton(frame, text="Select",
                          command=lambda i=index: self.select_configuration(i)
                          ).pack(side="right", padx=5)

            ctk.CTkButton(frame, text="Edit",
                          command=lambda i=index: self.edit_configuration(i)
                          ).pack(side="right", padx=5)

            ctk.CTkButton(frame, text="Delete",
                          command=lambda i=index: self.delete_configuration(i)
                          ).pack(side="right", padx=5)

        self.update_current_label()

    def update_current_label(self):
        if self.controller.selected_configuration is not None:
            name = self.configurations[self.controller.selected_configuration]["name"]
            self.current_label.configure(text=f"Current: {name}")
        else:
            self.current_label.configure(text="No configuration selected")

    def select_configuration(self, index):
        self.controller.selected_configuration = index
        self.refresh()

    def delete_configuration(self, index):
        del self.configurations[index]
        self.controller.selected_configuration = None
        self.save_configurations()
        self.refresh()

    def create_configuration(self):
        new_config = {
            "name": f"New Configuration {len(self.configurations)+1}",
            "scales": []
        }
        self.configurations.append(new_config)
        self.controller.frames["EditTimetableConfigFrame"].set_configuration(
            len(self.configurations)-1,
            new_config,
            is_new=True
        )
        self.controller.show_frame("EditTimetableConfigFrame")

    def edit_configuration(self, index):
        config = self.configurations[index]
        self.controller.frames["EditTimetableConfigFrame"].set_configuration(
            index,
            config,
            is_new=False
        )
        self.controller.show_frame("EditTimetableConfigFrame")
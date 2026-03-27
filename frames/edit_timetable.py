import customtkinter as ctk

class EditTimetableConfigFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        self.current_index = None
        self.is_new = False
        self.scale_rows = []

        ctk.CTkLabel(self, text="Edit Configuration",
                     font=("Helvetica", 22, "bold")).pack(pady=10)

        self.name_entry = ctk.CTkEntry(self, width=300)
        self.name_entry.pack(pady=10)

        self.scroll = ctk.CTkScrollableFrame(self, height=250)
        self.scroll.pack(fill="both", expand=True, padx=20, pady=10)

        ctk.CTkButton(self, text="+ Add Scale",
                      command=self.add_scale_row).pack(pady=5)

        btn_frame = ctk.CTkFrame(self)
        btn_frame.pack(pady=10)

        ctk.CTkButton(btn_frame, text="Cancel",
                      command=self.cancel).pack(side="left", padx=10)

        ctk.CTkButton(btn_frame, text="Confirm",
                      command=self.confirm).pack(side="left", padx=10)

    # ----------------------------
    # Configuration Setup
    # ----------------------------

    def set_configuration(self, index, config, is_new=False):
        self.current_index = index
        self.is_new = is_new

        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, config["name"])

        for row in self.scale_rows:
            row.destroy()
        self.scale_rows.clear()

        for scale in config["scales"]:
            self.add_scale_row(scale)

    # ----------------------------
    # Scale Rows
    # ----------------------------

    def add_scale_row(self, scale_data=None):
        frame = ctk.CTkFrame(self.scroll)
        frame.pack(fill="x", pady=5)

        scale_entry = ctk.CTkEntry(frame, width=100)
        scale_entry.pack(side="left", padx=5)

        key_entry = ctk.CTkEntry(frame, width=50)
        key_entry.pack(side="left", padx=5)

        duration_entry = ctk.CTkEntry(frame, width=50)
        duration_entry.pack(side="left", padx=5)

        if scale_data:
            scale_entry.insert(0, scale_data["scale"])
            key_entry.insert(0, scale_data["key"])
            duration_entry.insert(0, scale_data["duration"])

        ctk.CTkButton(frame, text="X",
                      width=30,
                      command=lambda: self.delete_row(frame)
                      ).pack(side="left", padx=5)

        self.scale_rows.append(frame)

    def delete_row(self, frame):
        frame.destroy()
        self.scale_rows.remove(frame)

    # ----------------------------
    # Save / Cancel
    # ----------------------------

    def cancel(self):
        if self.is_new:
            timetable = self.controller.frames["TimetableConfigFrame"]
            del timetable.configurations[self.current_index]

        self.controller.show_frame("TimetableConfigFrame")

    def confirm(self):
        timetable = self.controller.frames["TimetableConfigFrame"]

        scales = []
        for row in self.scale_rows:
            entries = row.winfo_children()
            scales.append({
                "scale": entries[0].get(),
                "key": entries[1].get(),
                "duration": int(entries[2].get() or 1),
                "timescale": "Hours"
            })

        timetable.configurations[self.current_index] = {
            "name": self.name_entry.get(),
            "scales": scales
        }

        timetable.save_configurations()
        timetable.refresh()
        self.controller.show_frame("TimetableConfigFrame")
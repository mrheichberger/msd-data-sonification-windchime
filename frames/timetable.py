import customtkinter as ctk
import json
from datetime import datetime

import chime_update


class TimetableConfigFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)

        self.controller = controller
        self.configurations = []

        # layout balance
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(2, weight=1)

        # ---------------- HEADER ----------------
        ctk.CTkLabel(self, text="Timetable Configurations",
                     font=("Helvetica", 22, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        self.current_label = ctk.CTkLabel(self, text="")
        self.current_label.grid(row=1, column=0, columnspan=2)

        # ---------------- LEFT ----------------
        self.scroll = ctk.CTkScrollableFrame(self)
        self.scroll.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        # ---------------- RIGHT ----------------
        self.timeline = ctk.CTkScrollableFrame(self)
        self.timeline.grid(row=2, column=1, sticky="nsew", padx=10, pady=10)

        # ---------------- BUTTONS ----------------
        btn = ctk.CTkFrame(self)
        btn.grid(row=3, column=0, columnspan=2, pady=10)

        ctk.CTkButton(btn, text="Create",
                      command=self.create_configuration).pack(side="left", padx=10)

        ctk.CTkButton(btn, text="Home",
                      command=lambda: controller.show_frame("HomeFrame")).pack(side="left", padx=10)

        self.load()

    def on_show(self):
        self.refresh()

    # =========================
    # FILE HANDLING
    # =========================
    def load(self):
        try:
            with open("timetable_configs.json", "r") as f:
                self.configurations = json.load(f)
        except:
            self.configurations = []

    def save(self):
        with open("timetable_configs.json", "w") as f:
            json.dump(self.configurations, f, indent=4)

    # =========================
    # MAIN REFRESH
    # =========================
    def refresh(self):
        for w in self.scroll.winfo_children():
            w.destroy()

        for i, config in enumerate(self.configurations):
            frame = ctk.CTkFrame(self.scroll)
            frame.pack(fill="x", pady=5)

            # GRID LAYOUT 
            frame.grid_columnconfigure(0, weight=1)
            frame.grid_columnconfigure(1, weight=0)
            frame.grid_columnconfigure(2, weight=0)
            frame.grid_columnconfigure(3, weight=0)

            # NAME
            ctk.CTkLabel(
                frame,
                text=config["name"],
                anchor="w"
            ).grid(row=0, column=0, sticky="w", padx=10, pady=5)

            # DELETE CONFIG
            ctk.CTkButton(
                frame,
                text="Delete",
                width=70,
                fg_color="#aa3333",
                hover_color="#882222",
                command=lambda i=i: self.delete_config(i)
            ).grid(row=0, column=1, padx=5, pady=5)

            # EDIT
            ctk.CTkButton(
                frame,
                text="Edit",
                width=70,
                command=lambda i=i: self.edit(i)
            ).grid(row=0, column=2, padx=5, pady=5)

            # SELECT
            ctk.CTkButton(
                frame,
                text="Select",
                width=70,
                command=lambda i=i: self.select(i)
            ).grid(row=0, column=3, padx=5, pady=5)

        self.update_label()
        self.update_timeline()

    # =========================
    # LABEL
    # =========================
    '''
    def update_label(self):
        if self.controller.selected_configuration is not None:
            name = self.configurations[self.controller.selected_configuration]["name"]
            self.current_label.configure(text=f"Current: {name}")
        else:
            self.current_label.configure(text="None selected")
    '''
    #new old code below is for debug 
    
    '''
    def update_label(self):
        if self.controller.selected_configuration is not None:
            print("selected_configuration:", self.controller.selected_configuration)
            print("type:", type(self.controller.selected_configuration))
            print("configurations type:", type(self.configurations))

            config = self.controller.selected_configuration
            name = f"{config.get('scale')} ({config.get('key')})"
            self.current_label.configure(text=f"Current: {name}")
        else:
            self.current_label.configure(text="None selected")
            '''
    def update_label(self):
        selected = self.controller.selected_configuration

        if selected is None:
            self.current_label.configure(text="None selected")
            return

        if isinstance(selected, int):
            config = self.configurations[selected]
            name = config.get("name", f"{config.get('scale')} ({config.get('key')})")

        elif isinstance(selected, dict):
            name = f"{selected.get('scale')} ({selected.get('key')})"

        else:
            name = "Unknown"

        self.current_label.configure(text=f"Current: {name}")
    # =========================
    # TIMELINE
    # =========================
    def update_timeline(self):
        for w in self.timeline.winfo_children():
            w.destroy()

        if self.controller.selected_configuration is None:
            return

        config = self.configurations[self.controller.selected_configuration]

        sorted_entries = sorted(
            config["scales"],
            key=lambda x: datetime.strptime(
                f"{x['date']} {x['start_time']}",
                "%Y-%m-%d %H:%M"
            )
        )

        for i, e in enumerate(sorted_entries):
            frame = ctk.CTkFrame(self.timeline)
            frame.pack(fill="x", pady=5)

            txt = (
                f"{e['date']} | {e['start_time']} → {e['end_time']}\n"
                f"Scale: {e['scale']} | Key: {e['key']}"
            )

            ctk.CTkLabel(
                frame,
                text=txt,
                anchor="w",
                justify="left"
            ).pack(side="left", padx=10)

            # DELETE ENTRY
            ctk.CTkButton(
                frame,
                text="Delete",
                width=70,
                fg_color="#aa3333",
                hover_color="#882222",
                command=lambda i=i: self.delete_entry(i)
            ).pack(side="right", padx=5)

    # =========================
    # ACTIONS
    # =========================
    def select(self, i):
        self.controller.selected_configuration = i
        self.refresh()
        chime_update(self)

    def edit(self, i):
        self.controller.frames["EditTimetableConfigFrame"].set_configuration(
            i, self.configurations[i], False
        )
        self.controller.show_frame("EditTimetableConfigFrame")

    def create_configuration(self):
        new = {"name": f"Config {len(self.configurations)+1}", "scales": []}
        self.configurations.append(new)

        self.controller.frames["EditTimetableConfigFrame"].set_configuration(
            len(self.configurations)-1, new, True
        )
        self.controller.show_frame("EditTimetableConfigFrame")

    def delete_config(self, i):
        del self.configurations[i]
        self.controller.selected_configuration = None
        self.save()
        self.refresh()

    def delete_entry(self, index):
        config = self.configurations[self.controller.selected_configuration]

        sorted_entries = sorted(
            enumerate(config["scales"]),
            key=lambda x: datetime.strptime(
                f"{x[1]['date']} {x[1]['start_time']}",
                "%Y-%m-%d %H:%M"
            )
        )

        original_index = sorted_entries[index][0]

        del config["scales"][original_index]

        self.save()
        self.refresh()
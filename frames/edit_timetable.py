import customtkinter as ctk
from datetime import datetime
from tkcalendar import DateEntry

import chime_update


class EditTimetableConfigFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)

        self.controller = controller
        self.config = None
        self.index = None

        self.grid_rowconfigure(6, weight=1)  # entries expand
        self.grid_columnconfigure(0, weight=1)
        
        # ---------------- HEADER ----------------
        ctk.CTkLabel(self, text="Edit Configuration",
                     font=("Helvetica", 20)).grid(row=0, column=0, pady=10)

        # ---------------- NAME ----------------
        self.name_entry = ctk.CTkEntry(self, placeholder_text="Name")
        self.name_entry.grid(row=1, column=0, pady=5, sticky="ew")

        # ---------------- DATE ----------------
        self.date = DateEntry(
            self,
            width=12,
            background='darkblue',
            foreground='white',
            borderwidth=2,
            date_pattern='yyyy-mm-dd'
        )
        self.date.grid(row=2, column=0, pady=5)

        # ---------------- TIME INPUTS ----------------
        time_frame = ctk.CTkFrame(self)
        time_frame.grid(row=3, column=0, pady=10, sticky="ew")

        minute_values = [f"{i:02d}" for i in range(0, 60, 5)]

        # START
        ctk.CTkLabel(time_frame, text="Start").grid(row=0, column=0, padx=5)

        self.start_hour = ctk.CTkOptionMenu(time_frame,
                                            values=[str(i) for i in range(1, 13)])
        self.start_hour.grid(row=0, column=1)

        self.start_minute = ctk.CTkOptionMenu(time_frame,
                                              values=minute_values)
        self.start_minute.grid(row=0, column=2)

        self.start_ampm = ctk.CTkOptionMenu(time_frame,
                                            values=["AM", "PM"])
        self.start_ampm.grid(row=0, column=3)

        # END
        ctk.CTkLabel(time_frame, text="End").grid(row=1, column=0, padx=5)

        self.end_hour = ctk.CTkOptionMenu(time_frame,
                                          values=[str(i) for i in range(1, 13)])
        self.end_hour.grid(row=1, column=1)

        self.end_minute = ctk.CTkOptionMenu(time_frame,
                                            values=minute_values)
        self.end_minute.grid(row=1, column=2)

        self.end_ampm = ctk.CTkOptionMenu(time_frame,
                                          values=["AM", "PM"])
        self.end_ampm.grid(row=1, column=3)

        # ---------------- SCALE + KEY ----------------
        sk_frame = ctk.CTkFrame(self)
        sk_frame.grid(row=4, column=0, pady=10)

        self.scale = ctk.CTkOptionMenu(
            sk_frame, values=["Major", "Minor", "Blues", "Suspended", "Pentatonic", "Custom"]
        )
        self.scale.pack(side="left", padx=5)

        self.key = ctk.CTkOptionMenu(
            sk_frame, values=["C", "D", "E", "F"]
        )
        self.key.pack(side="left", padx=5)

        # ---------------- ADD BUTTON ----------------
        ctk.CTkButton(self, text="Add Entry",
                      command=self.add_entry).grid(row=5, column=0, pady=10)

        # ---------------- ENTRY LIST ----------------
        self.entries_frame = ctk.CTkScrollableFrame(self)
        self.entries_frame.grid(row=6, column=0, sticky="nsew", padx=10, pady=10)

        # ---------------- BUTTON ROW ----------------
        button_row = ctk.CTkFrame(self)
        button_row.grid(row=7, column=0, pady=10, sticky="ew")
        button_row.background_color="transparent"

        ctk.CTkButton(button_row, text="Save",
                      command=self.save).pack(side="left", padx=10)

        ctk.CTkButton(button_row, text="Back",
                      command=lambda: controller.show_frame("TimetableConfigFrame")
                      ).pack(side="left", padx=10)

        # DEFAULTS
        self.start_hour.set("12")
        self.start_minute.set("00")
        self.start_ampm.set("AM")

        self.end_hour.set("12")
        self.end_minute.set("00")
        self.end_ampm.set("AM")

    # =========================
    # SET CONFIG
    # =========================
    def set_configuration(self, index, config, is_new):
        self.index = index
        self.config = config

        self.name_entry.delete(0, "end")
        self.name_entry.insert(0, config["name"])

        self.refresh_entries()

    # =========================
    # TIME CONVERSION
    # =========================
    def convert_to_24h(self, hour, minute, ampm):
        hour = int(hour)
        minute = int(minute)

        if ampm == "PM" and hour != 12:
            hour += 12
        if ampm == "AM" and hour == 12:
            hour = 0

        return f"{hour:02d}:{minute:02d}"

    def to_12h(self, time_str):
        h, m = map(int, time_str.split(":"))
        ampm = "AM" if h < 12 else "PM"
        h = h % 12 or 12
        return f"{h}:{m:02d} {ampm}"

    # =========================
    # ADD ENTRY
    # =========================
    def add_entry(self):
        try:
            date_val = self.date.get()

            start_time = self.convert_to_24h(
                self.start_hour.get(),
                self.start_minute.get(),
                self.start_ampm.get()
            )

            end_time = self.convert_to_24h(
                self.end_hour.get(),
                self.end_minute.get(),
                self.end_ampm.get()
            )

            datetime.strptime(date_val, "%Y-%m-%d")

        except:
            print("Invalid input")
            return

        entry = {
            "date": date_val,
            "start_time": start_time,
            "end_time": end_time,
            "scale": self.scale.get(),
            "key": self.key.get()
        }

        self.config["scales"].append(entry)
        self.refresh_entries()

    # =========================
    # DELETE ENTRY
    # =========================
    def delete_entry(self, index):
        del self.config["scales"][index]
        self.refresh_entries()

    # =========================
    # DISPLAY ENTRIES
    # =========================
    def refresh_entries(self):
        for w in self.entries_frame.winfo_children():
            w.destroy()

        for i, e in enumerate(self.config["scales"]):
            frame = ctk.CTkFrame(self.entries_frame)
            frame.pack(fill="x", pady=2)

            start_12 = self.to_12h(e["start_time"])
            end_12 = self.to_12h(e["end_time"])

            txt = (
                f"{e['date']} | {start_12} → {end_12} | "
                f"{e['scale']} {e['key']}"
            )

            ctk.CTkLabel(frame, text=txt).pack(side="left", padx=5)

            ctk.CTkButton(
                frame,
                text="Delete",
                width=70,
                fg_color="#aa3333",
                hover_color="#882222",
                command=lambda i=i: self.delete_entry(i)
            ).pack(side="right", padx=5)

    # =========================
    # SAVE
    # =========================
    def save(self):
        self.config["name"] = self.name_entry.get()

        parent = self.controller.frames["TimetableConfigFrame"]
        parent.save()
        parent.refresh()
        chime_update(self)

        self.controller.show_frame("TimetableConfigFrame")
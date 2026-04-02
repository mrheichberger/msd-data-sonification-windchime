import customtkinter as ctk

class PresetConfigFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller

        ctk.CTkLabel(self, text="Preset Configurations",
                     font=("Helvetica", 22, "bold")).pack(pady=20)

        self.presets = [
            {"name": "Sunny Mood", "scales": [{"scale": "Major", "key": "C", "duration": 2, "timescale": "Hours"}]},
            {"name": "Rainy Mood", "scales": [{"scale": "Minor", "key": "D", "duration": 1, "timescale": "Hours"}]},
        ]

        for preset in self.presets:
            ctk.CTkButton(self,
                          text=preset["name"],
                          command=lambda p=preset: self.apply_preset(p)
                          ).pack(pady=5)

        ctk.CTkButton(self,
                      text="Go Home",
                      command=lambda: controller.show_frame("HomeFrame")
                      ).pack(pady=20)

    def apply_preset(self, preset):
        timetable = self.controller.frames["TimetableConfigFrame"]
        timetable.configurations.append(preset)
        timetable.save_configurations()
        timetable.refresh()
        self.controller.show_frame("TimetableConfigFrame")
import customtkinter as ctk
import json
import os


class WeatherMoodFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)

        self.controller = controller

        # ---------------- OPTIONS ----------------
        self.weather_options = ["Sunny", "Rainy", "Cloudy", "Stormy", "Snowy"]
        self.temp_options = ["<25", "25-50", "50-75", "75+"]
        self.scale_options = ["Major", "Minor", "Blues", "Suspended", "Pentatonic", "Custom"]
        self.key_options = ["C", "D", "E", "F"]

        # ---------------- GRID SETUP ----------------
        for i in range(4):
            self.grid_columnconfigure(i, weight=1)

        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        # ---------------- ROW 0: DROPDOWNS ----------------
        self.weather_dropdown = ctk.CTkOptionMenu(self, values=self.weather_options)
        self.weather_dropdown.grid(row=0, column=0, padx=10, pady=20, sticky="ew")

        self.temp_dropdown = ctk.CTkOptionMenu(self, values=self.temp_options)
        self.temp_dropdown.grid(row=0, column=1, padx=10, pady=20, sticky="ew")

        self.scale_dropdown = ctk.CTkOptionMenu(
            self,
            values=self.scale_options,
            command=self.scale_changed
        )
        self.scale_dropdown.grid(row=0, column=2, padx=10, pady=20, sticky="ew")

        self.key_dropdown = ctk.CTkOptionMenu(self, values=self.key_options)
        self.key_dropdown.grid(row=0, column=3, padx=10, pady=20, sticky="ew")

        # ---------------- ROW 1: BUTTONS ----------------
        self.apply_button = ctk.CTkButton(self, text="Apply", command=self.apply_settings)
        self.apply_button.grid(row=1, column=1, padx=10, pady=20, sticky="ew")

        self.back_button = ctk.CTkButton(
            self,
            text="Back",
            command=lambda: controller.show_frame("HomeFrame")
        )
        self.back_button.grid(row=1, column=2, padx=10, pady=20, sticky="ew")

    # ---------------- SCALE LOGIC ----------------
    def scale_changed(self, choice):
        if choice == "Custom":
            self.key_dropdown.grid_remove()
        else:
            self.key_dropdown.grid()

    # ---------------- SAVE CONFIG ----------------
    def apply_settings(self):
        print("[WEATHER_MOOD] Applying weather mood settings")
        weather = self.weather_dropdown.get()
        temp = self.temp_dropdown.get()
        scale = self.scale_dropdown.get()
        key = None if scale == "Custom" else self.key_dropdown.get()

        # Store globally
        self.controller.selected_configuration = {
            "weather": weather,
            "temperature": temp,
            "scale": scale,
            "key": key
        }

        # ---------------- JSON FILE ----------------
        #os.makedirs("data", exist_ok=True)

        filename = "weather_mood_config.json"
        filepath = os.path.join("data", filename)

        json_key = f"{weather}_{temp}"

        # Load existing data
        data = {}
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                try:
                    data = json.load(f)
                except:
                    data = {}

        # Update entry
        data[json_key] = {
            "scale": scale,
            "key": key
        }

        # Save file
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)

        print(f"Saved to {filepath}")
        self.controller.run_backend_update(reason="weather mood config updated")

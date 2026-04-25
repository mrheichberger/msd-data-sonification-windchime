import customtkinter as ctk
import json
import os


class WeatherMoodFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)

        self.controller = controller

        # ---------------- STYLES ----------------
        self.dropdown_style = {
            "width": 150,
            "height": 40,
            "corner_radius": 10,
            "font": ("Helvetica", 18),
            "fg_color": "#F76902",
            "button_color": "#E65C00",
            "button_hover_color": "#BB4E00",
            "text_color": "#FFFFFF"
        }

        self.button_style = {
            "width": 150,
            "height": 40,
            "corner_radius": 10,
            "font": ("Helvetica", 16),
            "fg_color": "#F76902",
            "hover_color": "#BB4E00",
            "text_color": "#FFFFFF"
        }

        # ---------------- OPTIONS ----------------
        self.weather_options = ["Sunny", "Rainy", "Cloudy", "Stormy", "Snowy"]
        self.temp_options = ["<25", "25-50", "50-75", "75+"]
        self.scale_options = ["Major", "Minor", "Blues", "Suspended", "Pentatonic", "Custom"]
        self.key_options = ["C", "D", "E", "F"]

        # ---------------- MAIN GRID ----------------
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)

        # ================= DROPDOWN CONTAINER =================
        dropdown_container = ctk.CTkFrame(self)
        dropdown_container.grid(row=0, column=0, padx=20, pady=20)

        for i in range(2):
            dropdown_container.grid_columnconfigure(i, weight=1)

        # ---------------- LABELED DROPDOWNS ----------------
        self.weather_dropdown = self.create_labeled_dropdown(
            dropdown_container, "Weather", self.weather_options, 0, 0
        )

        self.temp_dropdown = self.create_labeled_dropdown(
            dropdown_container, "Temperature", self.temp_options, 0, 1
        )

        self.scale_dropdown = self.create_labeled_dropdown(
            dropdown_container, "Scale", self.scale_options, 1, 0, self.scale_changed
        )

        self.key_dropdown = self.create_labeled_dropdown(
            dropdown_container, "Key", self.key_options, 1, 1
        )

        # ================= BUTTON CONTAINER =================
        button_container = ctk.CTkFrame(self)
        button_container.grid(row=1, column=0, pady=20)

        button_container.grid_columnconfigure((0, 1), weight=1)

        self.apply_button = ctk.CTkButton(
            button_container,
            text="Apply",
            command=self.apply_settings,
            **self.button_style
        )
        self.apply_button.grid(row=0, column=0, padx=10, pady=10, sticky="ew")

        self.back_button = ctk.CTkButton(
            button_container,
            text="Back",
            command=lambda: controller.show_frame("HomeFrame"),
            **self.button_style
        )
        self.back_button.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

    # ---------------- HELPER: LABELED DROPDOWN ----------------
    def create_labeled_dropdown(self, parent, label_text, values, row, col, command=None):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=row, column=col, padx=10, pady=10, sticky="ew")

        frame.grid_columnconfigure(0, weight=1)

        label = ctk.CTkLabel(
            frame,
            text=label_text,
            font=("Helvetica", 14),
            text_color="#AAAAAA"
        )
        label.grid(row=0, column=0, sticky="w", pady=(0, 5))

        dropdown = ctk.CTkOptionMenu(
            frame,
            values=values,
            command=command,
            **self.dropdown_style
        )
        dropdown.grid(row=1, column=0, sticky="ew")

        return dropdown

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

        self.controller.selected_configuration = {
            "weather": weather,
            "temperature": temp,
            "scale": scale,
            "key": key
        }

        filename = "weather_mood_config.json"
        filepath = os.path.join("data", filename)

        json_key = f"{weather}_{temp}"

        data = {}
        if os.path.exists(filepath):
            with open(filepath, "r") as f:
                try:
                    data = json.load(f)
                except:
                    data = {}

        data[json_key] = {
            "scale": scale,
            "key": key
        }

        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)

        print(f"Saved to {filepath}")
        self.controller.run_backend_update(reason="weather mood config updated")
import customtkinter as ctk
import json
import os


class ChimeConfigFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        
        self.controller = controller
        self.file_path = "chime_states.json"

        # Load saved states (if file exists)
        self.saved_states = self.load_states()

        # Store switch variables
        self.chime_states = {}

        button_style = {
            "fg_color": "#F76902",
            "hover_color": "#BB4E00",
            "text_color": "#FFFFFF"
        }
        
        # Title
        title = ctk.CTkLabel(self, text="Chime Configuration", font=("Arial", 20))
        title.pack(pady=10)

        # Frame to hold switches
        switch_frame = ctk.CTkFrame(self)
        switch_frame.pack(pady=10)

        # Letters A → R (18 total)
        letters = [chr(i) for i in range(ord('A'), ord('R') + 1)]

        for i, letter in enumerate(letters):
            var = ctk.BooleanVar(value=self.saved_states.get(letter, False))

            switch = ctk.CTkSwitch(
                switch_frame,
                text=f"Chime {letter}",
                variable=var
            )
            switch.grid(row=i // 3, column=i % 3, padx=10, pady=10, sticky="w")

            self.chime_states[letter] = var

        # Buttons
        button_frame = ctk.CTkFrame(self)
        button_frame.pack(pady=10)

        save_btn = ctk.CTkButton(
            button_frame,
            text="Save",
            command=self.save_states,
            **button_style
        )
        save_btn.grid(row=0, column=0, padx=10)

        load_btn = ctk.CTkButton(
            button_frame,
            text="Reload",
            command=self.reload_states,
            **button_style
        )
        load_btn.grid(row=0, column=1, padx=10)

        back_btn = ctk.CTkButton(
            button_frame,
            text="Back to Home",
            command=lambda: controller.show_frame("HomeFrame"),
            **button_style
        )
        back_btn.grid(row=0, column=2, padx=10)
    # -------------------------
    # JSON FUNCTIONS
    # -------------------------

    def load_states(self):
        """Load chime states from JSON file"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                print("Error loading chime states:", e)
                return {}
        return {}

    def save_states(self):
        """Save current switch states to JSON"""
        results = {k: v.get() for k, v in self.chime_states.items()}

        try:
            with open(self.file_path, "w") as f:
                json.dump(results, f, indent=4)

            print("Chime states saved:", results)

            # Optional: store globally in controller
            self.controller.chime_states = results

        except Exception as e:
            print("Error saving chime states:", e)

    def reload_states(self):
        """Reload states from JSON and update UI"""
        self.saved_states = self.load_states()

        for letter, var in self.chime_states.items():
            var.set(self.saved_states.get(letter, False))

        print("Chime states reloaded")
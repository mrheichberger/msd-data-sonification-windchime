import customtkinter as ctk
import json
import os


class ChimeConfigFrame(ctk.CTkFrame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        
        self.controller = controller
        self.file_path = "chime_states.json"

        # Load saved states (if file exists)
        self.state_names = [
            "Major",
            "Minor",
            "Blues",
            "Suspended",
            "Pentatonic",
            "Minor Pentatonic"
        ]
        self.current_state = ctk.StringVar(value=self.state_names[0])
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

        self.state_dropdown = ctk.CTkOptionMenu(
            self,
            values=self.state_names,
            variable=self.current_state,
            command=self.change_state,
            
            fg_color="#F76902",          
            button_color="#BB4E00",      
            button_hover_color="#9A3E00",

            dropdown_fg_color="#1E1E1E", 
            dropdown_hover_color="#F76902",
            dropdown_text_color="#FFFFFF",

            text_color="#FFFFFF"
        )
        self.state_dropdown.pack(pady=10)
        
        # Frame to hold switches
        switch_frame = ctk.CTkFrame(self)
        switch_frame.pack(pady=10)
        
        # Notes (16 total)
        notes = ["C4", "C#4", "D4", "D#4", "E4", "F4", "F#4", "G4", "G#4", "A4", "A#4", "B4",
                 "C5", "C#5", "D5", "D#5"]

        for i, note in enumerate(notes):
            var = ctk.BooleanVar()

            switch = ctk.CTkSwitch(
                switch_frame,
                text=f"Chime {note}",
                variable=var
            )
            switch.grid(row=i // 4, column=i % 4, padx=10, pady=10, sticky="w")

            self.chime_states[note] = var

        self.apply_state(self.current_state.get())
        
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
        back_btn = ctk.CTkButton(
            button_frame,
            text="Back to Home",
            command=lambda: controller.show_frame("HomeFrame"),
            **button_style
        )
        back_btn.grid(row=0, column=1, padx=10)
    # -------------------------
    # STATE HANDLING
    # -------------------------

    def change_state(self, selected_state):
        """Called when dropdown changes"""
        self.apply_state(selected_state)

    def apply_state(self, state_name):
        """Apply selected state to switches"""
        state_data = self.saved_states.get(state_name, {})

        for note, var in self.chime_states.items():
            var.set(state_data.get(note, False))

        print(f"Loaded {state_name}")

    # -------------------------
    # JSON FUNCTIONS
    # -------------------------

    def load_states(self):
        """Load all states from JSON"""
        if os.path.exists(self.file_path):
            try:
                with open(self.file_path, "r") as f:
                    return json.load(f)
            except Exception as e:
                print("Error loading:", e)
        return {}

    def save_states(self):
        """Save current selected state"""
        current = self.current_state.get()

        self.saved_states[current] = {
            k: v.get() for k, v in self.chime_states.items()
        }

        try:
            with open(self.file_path, "w") as f:
                json.dump(self.saved_states, f, indent=4)

            print(f"{current} saved:", self.saved_states[current])

            # Optional global access
            self.controller.chime_states = self.saved_states[current]

        except Exception as e:
            print("Error saving:", e)

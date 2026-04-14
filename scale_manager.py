import json


class ScaleManager:
    def __init__(self, scales_path, final_path):
        """
        Args:
            scales_path (str): path to saved scales JSON
            final_path (str): path to final live JSON
        """
        self.scales_path = scales_path
        self.final_path = final_path

    def load_scales(self):
        """Load all saved scales from chime_states.json."""
        with open(self.scales_path, "r") as f:
            return json.load(f)

    def load_final_notes(self):
        """Load the currently active final note JSON."""
        with open(self.final_path, "r") as f:
            return json.load(f)

    def save_final_notes(self, note_data):
        """
        Write the active 16-note state to final_notes.json.

        Args:
            note_data (dict): note dictionary with 16 true/false values
        """
        with open(self.final_path, "w") as f:
            json.dump(note_data, f, indent=4)

    def update_from_selection(self, scale_name, key_name=None):
        """
        Update final_notes.json from the chosen scale.

        Behavior:
        - If scale_name is "Custom", copy scales["Custom"]
        - Otherwise, copy scales[scale_name][key_name]

        Args:
            scale_name (str): e.g. "Major", "Minor", "Blues", "Custom"
            key_name (str | None): e.g. "C", "D", "E", "F"
        """
        scales = self.load_scales()

        if scale_name not in scales:
            raise ValueError(f"Scale '{scale_name}' not found.")

        # Special case: Custom is stored as a flat note dictionary
        if scale_name == "Custom":
            self.save_final_notes(scales["Custom"])
            return

        # All other scales require a key
        if key_name is None:
            raise ValueError(f"Key is required for scale '{scale_name}'.")

        if key_name not in scales[scale_name]:
            raise ValueError(f"Key '{key_name}' not found under scale '{scale_name}'.")

        self.save_final_notes(scales[scale_name][key_name])

        """
README:
This class loads note presets from chime_states.json and writes the active
16-note result to final_notes.json.

Stored scale formats:
- Normal scales are nested by key:
    scales["Major"]["C"]
    scales["Minor"]["D"]

- Custom is stored as one flat 16-note dictionary:
    scales["Custom"]

Behavior:
- If the selected scale is "Custom", key is ignored and Custom is copied
  directly into final_notes.json.
- Otherwise, the selected scale and key are used to find the matching
  16-note preset and write it into final_notes.json.

This allows both:
1. keyed musical presets like Major in C, D, E, F
2. one saved Custom preset
"""
import json

'''takes jason file chime_states adn '''
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

    def update_from_scale(self, scale_name):
        """
        Copy one named scale from chime_states.json into final_notes.json.

        Args:
            scale_name (str): e.g. 'Major', 'Minor'
        """
        scales = self.load_scales()

        if scale_name not in scales:
            raise ValueError(f"Scale '{scale_name}' not found.")

        self.save_final_notes(scales[scale_name])

    def update_from_user_defined(self, user_notes):
        """
        Copy user-defined note selections directly into final_notes.json.

        Args:
            user_notes (dict): 16-note true/false dictionary
        """
        self.save_final_notes(user_notes)
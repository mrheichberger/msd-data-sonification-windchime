import json

'''
This will read the notes from the file: final_truth
and it will map the notes that are either turned on and 
off to the 6 position geneva mechanism where slot 0 would be facing towards you and then slot 2 is upper left and 
slot 4 is upper right position. 
Slots numbered 0-5 and 0 is no chimes, slot 2/B  is the "note 1" and slot 4/D is "note 2" and slot 3/C is both notes on
and then slot 0 is A where no notes are being played '''

import json


class ChimeMapper:
    def __init__(self, final_path):
        """
        Args:
            final_path (str): path to final_truth.json
        """
        self.final_path = final_path

        # Mechanical pair layout (8 actuators)
        self.pairs = [
            ("C4", "C#4"),
            ("D4", "D#4"),
            ("E4", "F4"),
            ("F#4", "G4"),
            ("G#4", "A4"),
            ("A#4", "B4"),
            ("C5", "C#5"),
            ("D5", "D#5"),
        ]

    def load_final_notes(self):
        """
        Load the active final note state from final_truth.json.
        """
        try:
            with open(self.final_path, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Could not find {self.final_path}")

    def get_position(self, note_1, note_2):
        """
        Convert two booleans into an encoder position.

        Mapping:
            A (none)        -> 0
            B (first only)  -> 2
            C (both)        -> 3
            D (second only) -> 4
        """
        if note_1 and note_2:
            return 4
        elif note_1:
            return 3
        elif note_2:
            return 5
        else:
            return 1

    def map_final_notes_to_positions(self, debug=False):
        """
        Read final_truth.json and convert it into 8 encoder positions.

        Args:
            debug (bool): print mapping details

        Returns:
            list[int]: 8 encoder positions
        """
        notes = self.load_final_notes()
        positions = []

        for note_1, note_2 in self.pairs:
            val_1 = notes.get(note_1, False)
            val_2 = notes.get(note_2, False)

            pos = self.get_position(val_1, val_2)
            positions.append(pos)

            if debug:
                print(f"{note_1}/{note_2} -> ({val_1}, {val_2}) -> {pos}")

        return positions


# 🔥 THIS is what makes "python chime_mapper.py" actually print something
if __name__ == "__main__":
    mapper = ChimeMapper("final_truth.json")

    print("Mapping final_truth.json → encoder positions...\n")

    positions = mapper.map_final_notes_to_positions(debug=True)

    print("\nFinal Positions:")
    print(positions)

'''this correctly returns the amount of geneva movements from 0 = no chimes being played'''
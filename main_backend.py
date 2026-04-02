''' 
This file will deciede if the the chime is 
in user or weather mode. 
If in user mode, take the user definded scale and
update the final json with that. 
If weather mode, take the weather scale and 
update the final json. 
'''
from scale_manager import ScaleManager
from chime_mapper import ChimeMapper
from weather_mode_mapper import WeatherModeMapper


# File paths
SCALES_PATH = "chime_states.json"
FINAL_PATH = "final_notes.json"


def update_final_json(control_mode, weather_data=None, user_notes=None):
    """
    Update final_notes.json based on control mode.

    Args:
        control_mode (str): 'weather' or 'user'
        weather_data (dict): OpenWeather JSON
        user_notes (dict): 16-note custom UI dictionary
    """
    scale_manager = ScaleManager(SCALES_PATH, FINAL_PATH)

    if control_mode == "weather":
        if weather_data is None:
            raise ValueError("weather_data is required for weather mode.")

        weather_mapper = WeatherModeMapper()
        scale_name = weather_mapper.get_scale_name(weather_data)

        print(f"Weather selected scale: {scale_name}")
        scale_manager.update_from_scale(scale_name)

    elif control_mode == "user":
        if user_notes is None:
            raise ValueError("user_notes is required for user mode.")

        print("Using user-defined note selections.")
        scale_manager.update_from_user_defined(user_notes)

    else:
        raise ValueError("control_mode must be 'weather' or 'user'")


def get_encoder_positions():
    """
    Read final_notes.json and return the 8 encoder positions.
    """
    mapper = ChimeMapper(FINAL_PATH)
    return mapper.map_final_notes_to_positions()


if __name__ == "__main__":
    # Example 1: weather mode
    fake_weather_data = {
        "current": {
            "weather": [
                {"main": "Rain"}
            ]
        }
    }

    update_final_json(control_mode="weather", weather_data=fake_weather_data)
    print("Positions after weather update:", get_encoder_positions())

    # Example 2: user-defined mode
    user_defined_notes = {
        "C4": False,
        "C#4": True,
        "D4": False,
        "D#4": False,
        "E4": False,
        "F4": True,
        "F#4": False,
        "G4": False,
        "G#4": False,
        "A4": False,
        "A#4": True,
        "B4": False,
        "C5": False,
        "C#5": False,
        "D5": False,
        "D#5": False
    }

    update_final_json(control_mode="user", user_notes=user_defined_notes)
    print("Positions after user update:", get_encoder_positions())
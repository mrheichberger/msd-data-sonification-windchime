'''
This file decides if the chime is
in user mode or weather mode.

If in weather mode:
- use weather data to choose scale + key
- then update final_notes.json from chime_states.json

If in user mode:
- use the GUI-selected scale choice
- if it is a normal scale, use scale + key
- if it is Custom, copy the Custom note set
'''

from scale_manager import ScaleManager
from chime_mapper import ChimeMapper
from weather_mode_mapper import WeatherModeMapper


# File paths
SCALES_PATH = "chime_states.json"
FINAL_PATH = "final_notes.json"


def update_final_json(control_mode, weather_data=None, selected_scale=None, selected_key=None):
    """
    Update final_notes.json based on control mode.

    Args:
        control_mode (str): 'weather' or 'user'
        weather_data (dict): OpenWeather JSON for weather mode
        selected_scale (str): GUI-selected scale for user mode
        selected_key (str): GUI-selected key for user mode
    """
    scale_manager = ScaleManager(SCALES_PATH, FINAL_PATH)

    if control_mode == "weather":
        if weather_data is None:
            raise ValueError("weather_data is required for weather mode.")

        weather_mapper = WeatherModeMapper()
        result = weather_mapper.get_scale_and_key(weather_data)

        scale_name = result["scale"]
        key_name = result["key"]

        print(f"Weather selected scale: {scale_name}")
        print(f"Weather selected key: {key_name}")

        scale_manager.update_from_selection(scale_name, key_name)

    elif control_mode == "user":
        if selected_scale is None:
            raise ValueError("selected_scale is required for user mode.")

        print(f"User selected scale: {selected_scale}")

        if selected_scale == "Custom":
            scale_manager.update_from_selection("Custom")
        else:
            if selected_key is None:
                raise ValueError("selected_key is required for non-Custom user scales.")

            print(f"User selected key: {selected_key}")
            scale_manager.update_from_selection(selected_scale, selected_key)

    else:
        raise ValueError("control_mode must be 'weather' or 'user'")


def get_encoder_positions():
    """
    Read final_notes.json and return the encoder positions.
    """
    mapper = ChimeMapper(FINAL_PATH)
    return mapper.map_final_notes_to_positions()

#debug 
'''
if __name__ == "__main__":
    # Example 1: weather mode
    fake_weather_data = {
        "current": {
            "temp": 40,
            "weather": [
                {"main": "Rain"}
            ]
        }
    }

    update_final_json(control_mode="weather", weather_data=fake_weather_data)
    print("Positions after weather update:", get_encoder_positions())

    # Example 2: user mode with keyed scale
    update_final_json(control_mode="user", selected_scale="Major", selected_key="D")
    print("Positions after user Major D:", get_encoder_positions())

    # Example 3: user mode with Custom
    update_final_json(control_mode="user", selected_scale="Custom")
    print("Positions after user Custom:", get_encoder_positions())
    '''
from scale_manager import ScaleManager
from chime_mapper import ChimeMapper
from weather_mode_mapper import WeatherModeMapper
from datetime import datetime
import json


# File paths
SCALES_PATH = "data/chime_states.json"
FINAL_PATH = "data/final_notes.json"
TIMETABLE_PATH = "timetable_configs.json"


def get_active_scheduled_scale(timetable_path):
    """
    Return the currently active scheduled scale entry if one exists.
    Otherwise return None.
    """
    now = datetime.now()
    current_date = now.date()
    current_time = now.time()

    with open(timetable_path, "r") as f:
        configs = json.load(f)

    for config in configs:
        for entry in config.get("scales", []):
            entry_date = datetime.strptime(entry["date"], "%Y-%m-%d").date()
            start_time = datetime.strptime(entry["start_time"], "%H:%M").time()
            end_time = datetime.strptime(entry["end_time"], "%H:%M").time()

            if entry_date != current_date:
                continue

            # Normal same-day range
            if start_time <= end_time:
                if start_time <= current_time <= end_time:
                    return entry

            # Crosses midnight
            else:
                if current_time >= start_time or current_time <= end_time:
                    return entry

    return None


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

    if control_mode == "Weather Mode":
        if weather_data is None:
            raise ValueError("weather_data is required for weather mode.")

        weather_mapper = WeatherModeMapper()
        result = weather_mapper.get_scale_and_key(weather_data)

        scale_name = result["scale"]
        key_name = result["key"]

        print(f"Weather selected scale: {scale_name}")
        print(f"Weather selected key: {key_name}")

        scale_manager.update_from_selection(scale_name, key_name)

    elif control_mode == "User Mode":
        scheduled_entry = get_active_scheduled_scale(TIMETABLE_PATH)

        if scheduled_entry is not None:
            scale_name = scheduled_entry["scale"]
            key_name = scheduled_entry.get("key")

            print(f"Scheduled user scale active: {scale_name}")
            print(f"Scheduled user key active: {key_name}")

            if scale_name == "Custom":
                scale_manager.update_from_selection("Custom")
            else:
                if key_name is None:
                    raise ValueError("Scheduled keyed scale is missing a key.")
                scale_manager.update_from_selection(scale_name, key_name)

        else:
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
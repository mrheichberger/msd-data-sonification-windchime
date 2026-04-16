#test_full_pipeline.py

import json
from main_backend import update_final_json, get_encoder_positions

FINAL_PATH = "final_notes.json"


def print_final_json():
    with open(FINAL_PATH, "r") as f:
        data = json.load(f)

    print("\nUpdated final_notes.json:")
    print(json.dumps(data, indent=4))


def run_test(control_mode, weather_data=None, selected_scale=None, selected_key=None):
    print("\n" + "=" * 50)
    print(f"TESTING MODE: {control_mode}")

    if selected_scale:
        print(f"Selected scale: {selected_scale}")
    if selected_key:
        print(f"Selected key: {selected_key}")
    if weather_data:
        print(f"Weather data: {weather_data}")

    update_final_json(
        control_mode=control_mode,
        weather_data=weather_data,
        selected_scale=selected_scale,
        selected_key=selected_key
    )

    print_final_json()

    positions = get_encoder_positions()
    print("\nEncoder positions:")
    print(positions)

    print("=" * 50)


if __name__ == "__main__":
    # Test 1: user mode, normal keyed scale
    run_test(control_mode="user", selected_scale="Major", selected_key="D")

    # Test 2: user mode, custom
    run_test(control_mode="user", selected_scale="Custom")

    # Test 3: weather mode
    fake_weather_data = {
        "current": {
            "temp": 40,
            "weather": [{"main": "Rain"}]
        }
    }
    run_test(control_mode="weather", weather_data=fake_weather_data)
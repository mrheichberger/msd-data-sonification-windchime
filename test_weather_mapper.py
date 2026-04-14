'''from weather_mode_mapper import WeatherModeMapper

mapper = WeatherModeMapper("data/weather_mood_config.json")

fake_weather_data = {
    "current": {
        "temp": 40,
        "weather": [{"main": "Rain"}]
    }
}

result = mapper.get_scale_and_key(fake_weather_data)

print("Weather result:", result)
'''

#test scale manager 
'''
from scale_manager import ScaleManager

manager = ScaleManager(
    "data/chime_states.json",
    "final_notes.json"
)

manager.update_from_selection("Blues", "E")

print(manager.load_final_notes())
'''

#overall test 
from main_backend import update_final_json, get_encoder_positions

fake_weather_data = {
    "current": {
        "temp": 40,
        "weather": [{"main": "Rain"}]
    }
}

update_final_json(control_mode="weather", weather_data=fake_weather_data)

print("Encoder positions:", get_encoder_positions())
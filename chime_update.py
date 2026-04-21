import json
import datetime
import os
from services.weather_service import WeatherService
from current_chime_position import run_full_backend_update

weather_mood_config = "data/weather_mood_config.json"
chime_states = "data/chime_states.json"
timetable_config = "timetable_configs.json"

def get_weather_mood_config(weather_data):
    with open(weather_mood_config, "r") as f:
        weather_mood_data = json.load(f)
    
    
    # Process the weather data and update the application state
    scale, key = None, None
    
    condition = weather_data["current"]["weather"][0]["main"]
    temp = weather_data["current"]["temp"]
    
    condition_str = getCondition(condition)
    temp_range = get_temp_range(temp)
    
    table_key = f"{condition_str}_{temp_range}"
    print(f"Finding: {table_key}")
    
    config = weather_mood_data[table_key]
    scale = config["scale"]
    key = config["key"]
    
    return scale, key

def check_timetable(timetable_data, current_config):
    if current_config is None:
        return None
    
    now = datetime.datetime.now()
    current_time = now.strftime("%H:%M")
    
    for config in timetable_data:
        if config["name"] == current_config:
            start_time = config["start_time"]
            end_time = config["end_time"]
            
            if (start_time <= current_time <= end_time):
                return {"scale": config["scale"], "key": config["key"]}
    
    return None

def chime_update(self):

    with open(timetable_config, "r") as f:
        timetable_data = json.load(f)
    
    control_mode = self.current_mode 
    current_config = self.selected_configuration
    
    weather_service = WeatherService()
    weather_data, _ = weather_service.fetch_weather()
    self.weather = weather_data
    
    scale = None
    key = None
    timetable = check_timetable(timetable_data, current_config)
    if timetable is not None:
        print("Active timetable config found, using that...")
        scale = timetable["scale"]
        key = timetable["key"]
    else:
        print("No active timetable config found, checking weather...")
        scale, key = get_weather_mood_config(weather_data)
    
    #print(f"Updating with scale: {scale}, key: {key}")
    #run_full_backend_update(control_mode, weather_data, scale, key)
    
    

def get_temp_range(temp):
    if temp < 25:
        return "<25"
    elif temp < 50:
        return "25-50"
    elif temp < 75:
        return "50-75"
    else:
        return "75+"
    
def getCondition(condition):
    condition = condition.lower()
    if condition == "clear":
        return "Sunny"
    elif condition in [
        "clouds", "mist", "smoke", "haze", "fog",
        "dust", "sand", "ash"
    ]:
        return "Cloudy"
    elif condition in ["rainy", "drizzle"]:
        return "Rainy"
    elif condition == "snowy":
        return "Snowy"
    elif condition in ["thunderstorm", "squall", "tornado"]:
        return "Stormy"
    else: 
        # Default case for unrecognized conditions
        return "Cloudy"
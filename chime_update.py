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

    if current_config >= len(timetable_data):
        print("[TIMETABLE] Invalid config index")
        return None

    config = timetable_data[current_config]

    if not config.get("scales"):
        print(f"[TIMETABLE] No scales defined for config index: {current_config}")
        return None
    
    print(f"[TIMETABLE] Checking timetable for config index: {current_config}")
    
    for i in range(len(timetable_data[current_config]["scales"])):
        
        if (timetable_data[current_config]["scales"][i]["date"] != datetime.datetime.now().strftime("%Y-%m-%d")):
            print(f"[TIMETABLE] Skipping scale index {i} due to date mismatch")
            continue
        
        start_time = timetable_data[current_config]["scales"][i]["start_time"]
        end_time = timetable_data[current_config]["scales"][i]["end_time"]
        print (f"[TIMETABLE] Current time: {datetime.datetime.now().strftime('%H:%M')}, Start time: {start_time}, End time: {end_time}")
        
        now = datetime.datetime.now()
        current_time = now.strftime("%H:%M")
        
        if (start_time <= current_time <= end_time):
            print(f"[TIMETABLE] Current time is within the range for config index: {current_config}")
            scale = timetable_data[current_config]["scales"][i]["scale"]
            key = timetable_data[current_config]["scales"][i]["key"]
            return { "scale": scale, "key": key }
    
    print(f"[TIMETABLE] Current time is NOT within the range for config index: {current_config}")
    return None

def chime_update(self):
    print("[CHIME_UPDATE] Starting chime_update")

    with open(timetable_config, "r") as f:
        timetable_data = json.load(f)
    
    control_mode = self.current_mode 
    current_config = self.selected_configuration
    
    print("[CHIME_UPDATE] Fetching weather")
    weather_data, _ = self.weather_service.fetch_weather()
    previous_weather = getattr(self, "last_weather_snapshot", None)
    self.weather = weather_data
    self.last_weather_snapshot = weather_data

    weather_changed = previous_weather != weather_data
    print(f"[CHIME_UPDATE] weather_changed={weather_changed}")
    print(f"[CHIME_UPDATE] control_mode={control_mode}, current_config={current_config}")
    
    scale = None
    key = None
    timetable = check_timetable(timetable_data, current_config)
    if timetable is not None:
        print("[CHIME_UPDATE] Active timetable config found, using that...")
        scale = timetable["scale"]
        key = timetable["key"]
    else:
        print("[CHIME_UPDATE] No active timetable config found, checking weather...")
        scale, key = get_weather_mood_config(weather_data)
    
    print(f"[CHIME_UPDATE] Updating with scale={scale}, key={key}")
    #run_full_backend_update(
    #    control_mode,
    #    weather_data,
    #    scale,
    #    key,
    #    reason="weather changed" if weather_changed else "scheduled refresh"
    #)
    
    

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
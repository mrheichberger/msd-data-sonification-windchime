'''
This is to pull weather modes from the API 
and to map them to the scales that they will play. 

Later the scales still need to be converted to what
notes are true and what notes are false '''

# weather_mode_mapper.py

"""
weather_mode_mapper.py

Maps live weather data to a GUI-configured scale/key pair.

The GUI writes a JSON file like:
{
    "Sunny_<25": {"scale": "Major", "key": "F"},
    ...
}
"""

import json
import os


class WeatherModeMapper:
    def __init__(self, config_path="weather_mode_config.json"):
        """
        Args:
            config_path (str): path to GUI-written JSON config file
        """
        self.config_path = config_path
        self.weather_map = self.load_config()

    def load_config(self):
        """
        Load the GUI-written weather mapping file.

        Returns:
            dict: mapping like
                {
                    "Sunny_<25": {"scale": "Major", "key": "F"},
                    ...
                }
        """
        if not os.path.exists(self.config_path):
            print(f"Warning: config file '{self.config_path}' not found.")
            return {}

        try:
            with open(self.config_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading weather config: {e}")
            return {}

    def reload_config(self):
        """
        Reload config from disk in case GUI changed it while program is running.
        """
        self.weather_map = self.load_config()

    def get_condition_name(self, weather_data):
        """
        Convert OpenWeather 'main' condition into your GUI naming style.

        Args:
            weather_data (dict): JSON response from OpenWeather

        Returns:
            str: one of 'Sunny', 'Rainy', 'Cloudy', 'Stormy', 'Snowy'
        """
        current = weather_data.get("current", {})
        weather_list = current.get("weather", [])

        if not weather_list:
            return "Sunny"  # safe fallback

        main_condition = weather_list[0].get("main", "")

        if main_condition == "Thunderstorm":
            return "Stormy"
        if main_condition == "Snow":
            return "Snowy"
        if main_condition in ["Rain", "Drizzle"]:
            return "Rainy"
        if main_condition == "Clouds":
            return "Cloudy"
        if main_condition == "Clear":
            return "Sunny"

        # fog, mist, haze, etc.
        return "Cloudy"

    def get_temperature_bucket(self, weather_data):
        """
        Convert current temperature into one of your bucket labels.

        Assumes OpenWeather temperature is in Fahrenheit if your API request
        uses units=imperial.

        Args:
            weather_data (dict): JSON response from OpenWeather

        Returns:
            str: one of '<25', '25-50', '50-75', '75+'
        """
        current = weather_data.get("current", {})
        temp = current.get("temp", None)

        if temp is None:
            return "50-75"  # safe fallback

        if temp < 25:
            return "<25"
        elif temp < 50:
            return "25-50"
        elif temp < 75:
            return "50-75"
        else:
            return "75+"

    def get_lookup_key(self, weather_data):
        """
        Build the exact key used in the GUI config file.

        Example:
            'Sunny_50-75'
            'Rainy_<25'
        """
        condition = self.get_condition_name(weather_data)
        temp_bucket = self.get_temperature_bucket(weather_data)
        return f"{condition}_{temp_bucket}"

    def get_scale_and_key(self, weather_data):
        """
        Get the scale/key pair from the GUI config file.

        Args:
            weather_data (dict): JSON response from OpenWeather

        Returns:
            dict: {"scale": ..., "key": ...}
        """
        lookup_key = self.get_lookup_key(weather_data)

        if lookup_key in self.weather_map:
            return self.weather_map[lookup_key]

        # fallback if config entry missing
        return {
            "scale": "Major",
            "key": "C"
        }

    def get_scale(self, weather_data):
        """
        Convenience function if old backend expects only scale.
        """
        return self.get_scale_and_key(weather_data)["scale"]

    def get_key(self, weather_data):
        """
        Convenience function if backend also needs the selected key.
        """
        return self.get_scale_and_key(weather_data)["key"]
    
    """
======================== WEATHER MODE MAPPER ========================

OVERVIEW:
This module maps real-time weather data from the OpenWeather API
to a musical scale and key based on a configuration file generated
by the GUI.

Instead of hardcoding mappings (weather → scale), this system allows
the GUI to dynamically control how weather conditions translate into
musical behavior.

---------------------------------------------------------------------

HOW IT WORKS:

1. WEATHER DATA INPUT
   The mapper receives a JSON response from the OpenWeather API:
   {
       "current": {
           "temp": 63,
           "weather": [{"main": "Clouds"}]
       }
   }

2. CONDITION PARSING
   The weather condition is converted into one of:
       Sunny, Rainy, Cloudy, Stormy, Snowy

3. TEMPERATURE BUCKETING
   The temperature is grouped into one of four ranges:
       <25, 25-50, 50-75, 75+

4. LOOKUP KEY GENERATION
   These are combined into a key like:
       "Cloudy_50-75"

5. CONFIG FILE LOOKUP
   The key is used to index into a GUI-generated JSON file:
       {
           "Cloudy_50-75": {
               "scale": "Pentatonic",
               "key": "D"
           }
       }

6. OUTPUT
   The mapper returns:
       {
           "scale": "Pentatonic",
           "key": "D"
       }

---------------------------------------------------------------------

WHY THIS DESIGN:

- Removes hardcoded logic from the backend
- Allows the GUI to fully control musical behavior
- Makes it easy to tweak mappings without changing code
- Scales easily if new conditions or ranges are added

---------------------------------------------------------------------

FALLBACK BEHAVIOR:

- If weather data is missing → defaults to "Sunny"
- If temperature is missing → defaults to "50-75"
- If lookup key is missing → defaults to:
      scale = "Major", key = "C"

---------------------------------------------------------------------

NOTES:

- Assumes temperature is in Fahrenheit (OpenWeather: units=imperial)
- Call `reload_config()` if the GUI updates the JSON while running
- This module ONLY selects scale + key
  (note activation mapping is handled elsewhere)

=====================================================================
"""
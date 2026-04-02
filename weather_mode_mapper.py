'''
This is to pull weather modes from the API 
and to map them to the scales that they will play. 

Later the scales still need to be converted to what
notes are true and what notes are false '''

# weather_mode_mapper.py

class WeatherModeMapper:
    def __init__(self):
        """
        Maps OpenWeather conditions to your scale names.
        """
        self.mode_to_scale = {
            "clear": "Major",
            "cloudy": "Pentatonic",
            "rain": "Minor",
            "snow": "Blues",
            "storm": "Minor",   # change later if you add a 5th custom scale
        }

    def get_mode(self, weather_data):
        """
        Decide which weather mode the current conditions belong to.

        Args:
            weather_data (dict): JSON response from OpenWeather

        Returns:
            str: one of 'clear', 'cloudy', 'rain', 'snow', 'storm'
        """
        current = weather_data.get("current", {})
        weather_list = current.get("weather", [])

        if not weather_list:
            return "clear"  # safe fallback

        main_condition = weather_list[0].get("main", "")

        # Highest priority: storm
        if main_condition == "Thunderstorm":
            return "storm"

        # Snow
        if main_condition == "Snow":
            return "snow"

        # Rain or drizzle
        if main_condition in ["Rain", "Drizzle"]:
            return "rain"

        # Clouds
        if main_condition == "Clouds":
            return "cloudy"

        # Clear sky
        if main_condition == "Clear":
            return "clear"

        # Fallback for mist, fog, haze, etc.
        return "cloudy"

    def get_scale(self, weather_data):
        """
        Convert weather JSON directly into a scale name.

        Args:
            weather_data (dict): JSON response from OpenWeather

        Returns:
            str: scale name, like 'Major' or 'Minor'
        """
        mode = self.get_mode(weather_data)
        return self.mode_to_scale[mode]
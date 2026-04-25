import os
import requests
from dotenv import load_dotenv


class WeatherService:
    def __init__(self):
        self.api_keys = {}
        self.enabled = True

        if not os.path.exists("API_KEYS.env"):
            print("API_KEYS.env file not found. Weather service will be disabled.")
            self.enabled = False
            return

        load_dotenv("API_KEYS.env")

        self.api_keys["openweathermap"] = os.getenv("OPENWEATHERMAP")
        if not self.api_keys["openweathermap"]:
            print("OPENWEATHERMAP key not found in API_KEYS.env. Weather service will be disabled.")
            self.enabled = False
            return

    def fetch_weather(self):
        if not self.enabled:
            print("[WEATHER] Service disabled; returning empty weather data")
            return {}, None

        print("[WEATHER] Requesting current weather")
        weather = requests.get(
            "https://api.openweathermap.org/data/2.5/weather?lat=43.0826701&lon=-77.6729322&units=imperial&appid="
            + self.api_keys["openweathermap"],
            timeout=10
        ).json()

        print("[WEATHER] Requesting forecast")
        forecast = requests.get(
            "https://api.openweathermap.org/data/2.5/forecast?lat=43.0826701&lon=-77.6729322&units=imperial&appid="
            + self.api_keys["openweathermap"],
            timeout=10
        ).json()

        print("[WEATHER] Requesting AQI")
        aqi = requests.get(
            "https://api.openweathermap.org/data/2.5/air_pollution?lat=43.0826701&lon=-77.6729322&appid="
            + self.api_keys["openweathermap"],
            timeout=10
        ).json()['list'][-1]['main']['aqi']

        icon_code = weather["weather"][0]["icon"]
        icon_url = f"http://openweathermap.org/img/wn/{icon_code}@4x.png"

        weather_data = {
            "current": {
                "temp": weather["main"]["temp"],
                "weather": [
                    {
                        "main": weather["weather"][0]["main"],
                        "icon": icon_url
                    }
                ]
            },
            "extra": {
                "wind_speed": weather["wind"]["speed"],
                "wind_dir": weather["wind"]["deg"],
                "humidity": weather["main"]["humidity"],
                "pressure": weather["main"]["pressure"],
                "clouds": weather["clouds"]["all"],
                "visibility": weather["visibility"],
                "pop": forecast["list"][-1]["pop"] * 100,
                "aqi": aqi
            }
        }

        uv = None
        print(f"[WEATHER] Weather fetch complete: temp={weather_data['current']['temp']}, condition={weather_data['current']['weather'][0]['main']}")
        return weather_data, uv
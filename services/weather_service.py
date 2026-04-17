import os
import requests
from datetime import datetime
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
            return {}, None

        weather = requests.get(
            "https://api.openweathermap.org/data/2.5/weather?lat=43.0826701&lon=-77.6729322&units=imperial&appid="
            + self.api_keys["openweathermap"]
        ).json()

        forecast = requests.get(
            "https://api.openweathermap.org/data/2.5/forecast?lat=43.0826701&lon=-77.6729322&units=imperial&appid="
            + self.api_keys["openweathermap"]
        ).json()

        aqi = requests.get(
            "https://api.openweathermap.org/data/2.5/air_pollution?lat=43.0826701&lon=-77.6729322&appid="
            + self.api_keys["openweathermap"]
        ).json()['list'][-1]['main']['aqi']

        weather_data = {
            "condition": weather['weather'][0]['main'], # Possible values: Clear, Clouds, Rain, Drizzle, 
                                                        # Thunderstorm, Snow, Mist, Smoke, Haze, Dust, Fog, Sand, Ash, Squall, Tornado
            "wind_speed": weather['wind']['speed'],
            "wind_dir": weather['wind']['deg'],
            "temp": weather['main']['temp'],
            "humidity": weather['main']['humidity'],
            "pressure": weather['main']['pressure'],
            "clouds": weather['clouds']['all'],
            "visibility": weather['visibility'],
            "pop": forecast['list'][-1]['pop'] * 100,
            "aqi": aqi
        }
        
        uv = None
        return weather_data, uv
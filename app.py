import sys
import customtkinter as ctk

from frames.home import HomeFrame
from frames.timetable import TimetableConfigFrame
from frames.edit_timetable import EditTimetableConfigFrame
from frames.preset import PresetConfigFrame
from frames.mode_selection import ModeSelectionFrame
from frames.monitor import MonitorFrame
from frames.chime_config import ChimeConfigFrame
from frames.weather_mood import WeatherMoodFrame

from services.weather_service import WeatherService
#from services.mood_service import MoodService
#from services.tts_service import generate_lines

ctk.set_appearance_mode("dark")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.geometry("800x600")
        self.title("Windchimes")
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.current_mode = "Weather Mode"
        self.selected_configuration = None
        self.weather = {}
        self.uv = None

        self.weather_service = WeatherService()
        #self.mood_service = MoodService()

        if self.weather_service.enabled:
            self.after(100, self.update_weather)

        self.frames = {}

        for Frame in (
            HomeFrame,
            PresetConfigFrame,
            TimetableConfigFrame,
            EditTimetableConfigFrame,
            ModeSelectionFrame,
            MonitorFrame,
            ChimeConfigFrame, 
            WeatherMoodFrame
        ):
            frame = Frame(self, controller=self)
            self.frames[Frame.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("HomeFrame")

        self.bind("<Escape>", lambda e: self.destroy())

    def show_frame(self, frame_name: str):
        frame = self.frames[frame_name]
        frame.tkraise()

        if hasattr(frame, "on_show"):
            frame.on_show()


    def update_weather(self):
        self.weather, self.uv = self.weather_service.fetch_weather()
        #elf.mood = self.mood_service.calculate_mood(self.weather)
        self.after(1000 * 60 * 20, self.update_weather)

if __name__ == "__main__":
    #generate_lines()
    app = App()
    app.mainloop()
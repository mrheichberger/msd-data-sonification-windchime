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

from current_chime_position import run_full_backend_update
from services.weather_service import WeatherService

ctk.set_appearance_mode("dark")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("800x600")
        self.title("Windchimes")

        self.attributes("-fullscreen", True)
    
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.current_mode = "Weather Mode"
        self.selected_configuration = None
        self.selected_scale = None
        self.selected_key = None
        self.weather = {}
        self.uv = None

        self.weather_service = WeatherService()

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

    def run_backend_update(self):
        try:
            if self.current_mode == "Weather Mode":
                run_full_backend_update(
                    control_mode="weather",
                    weather_data=self.weather
                )
            else:
                run_full_backend_update(
                    control_mode="user",
                    selected_scale=self.selected_scale,
                    selected_key=self.selected_key
                )

            print("Backend update complete.")
            import json

            with open("data/final_notes.json", "r") as f:
                notes = json.load(f)
                print("FINAL NOTES:", notes)

        except Exception as e:
            print("Backend update error:", e)

    def set_mode(self, mode):
        self.current_mode = mode
        self.run_backend_update()

    def set_user_selection(self, scale, key=None):
        self.selected_scale = scale
        self.selected_key = key
        self.run_backend_update()

    def update_weather(self):
        try:
            from chime_update import chime_update  # adjust import

            chime_update(
                control_mode=self.current_mode,
                current_config=None
            )

            print("Weather + backend updated")

        except Exception as e:
            print("Update error:", e)

        finally:
            # 🔁 run again in 10 minutes
            self.after(1000 * 60 * 10, self.update_weather)


if __name__ == "__main__":
    app = App()
    app.mainloop()
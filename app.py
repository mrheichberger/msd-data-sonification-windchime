import sys
import customtkinter as ctk
import threading
import os
from tkinter import messagebox

from frames.home import HomeFrame
from frames.rotate_frame import RotateFrame
from frames.timetable import TimetableConfigFrame
from frames.edit_timetable import EditTimetableConfigFrame
from frames.preset import PresetConfigFrame
from frames.mode_selection import ModeSelectionFrame
from frames.monitor import MonitorFrame
from frames.chime_config import ChimeConfigFrame
from frames.weather_mood import WeatherMoodFrame

from current_chime_position import run_full_backend_update
from services.weather_service import WeatherService

from dotenv import load_dotenv


load_dotenv("API_KEYS.env")
ctk.set_appearance_mode("dark")

# -----------------------------
# PASSWORD / SESSION SETTINGS
# -----------------------------
APP_PASSWORD = os.getenv("PASSWORD")        # Change this
SESSION_TIMEOUT = 15 * 60 * 1000             # 15 minutes (milliseconds)


# -----------------------------
# MAIN APPLICATION
# -----------------------------
class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("800x600")
        self.title("Windchimes")
        self.attributes("-fullscreen", True)

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # -----------------------------
        # APP STATE
        # -----------------------------
        self.current_mode = "Weather Mode"
        self.selected_configuration = None
        self.selected_scale = None
        self.selected_key = None
        self.weather = {}
        self.uv = None
        self.last_weather_snapshot = None
        self.update_running = False
        self.session_timer = None
        self.lock_screen = None

        # -----------------------------
        # WEATHER SERVICE
        # -----------------------------
        self.weather_service = WeatherService()

        if self.weather_service.enabled:
            self.after(100, self.update_weather)

        # -----------------------------
        # FRAME STORAGE
        # -----------------------------
        self.frames = {}

        for Frame in (
            HomeFrame,
            PresetConfigFrame,
            TimetableConfigFrame,
            EditTimetableConfigFrame,
            ModeSelectionFrame,
            MonitorFrame,
            ChimeConfigFrame,
            WeatherMoodFrame,
            RotateFrame
        ):
            frame = Frame(self, controller=self)
            self.frames[Frame.__name__] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("HomeFrame")

        # Escape exits app
        self.bind("<Escape>", lambda e: self.destroy())

        # -----------------------------
        # SESSION TIMER
        # -----------------------------
        self.reset_session_timer()

        # Reset timer whenever user interacts
        self.bind_all("<Any-KeyPress>", self.reset_session_timer)
        self.bind_all("<Any-Button>", self.reset_session_timer)
        self.bind_all("<Motion>", self.reset_session_timer)

    # -----------------------------
    # SESSION CONTROL
    # -----------------------------
    def reset_session_timer(self, event=None):
        """Reset inactivity timer after any user activity."""
        if self.lock_screen:
            return  # Don't reset while locked

        if self.session_timer:
            self.after_cancel(self.session_timer)

        self.session_timer = self.after(
            SESSION_TIMEOUT,
            self.force_relogin
        )

    def force_relogin(self):
        """Lock screen while backend continues running."""
        if self.lock_screen:
            return  # Prevent multiple lock screens

        self.lock_screen = ctk.CTkToplevel(self)
        self.lock_screen.attributes("-fullscreen", True)
        self.lock_screen.attributes("-topmost", True)
        self.lock_screen.title("Session Locked")

        # Prevent closing
        self.lock_screen.protocol("WM_DELETE_WINDOW", lambda: None)

        self.lock_screen.grid_rowconfigure((0, 1, 2, 3), weight=1)
        self.lock_screen.grid_columnconfigure(0, weight=1)

        # Lock Title
        ctk.CTkLabel(
            self.lock_screen,
            text="Session Locked",
            font=("Helvetica", 40, "bold")
        ).grid(row=0, column=0, pady=(80, 20))

        # Message
        ctk.CTkLabel(
            self.lock_screen,
            text="Enter password to continue",
            font=("Helvetica", 22)
        ).grid(row=1, column=0)

        # Password entry
        password_entry = ctk.CTkEntry(
            self.lock_screen,
            show="*",
            width=300,
            height=50,
            font=("Helvetica", 22),
            placeholder_text="Password"
        )
        password_entry.grid(row=2, column=0, pady=20)

        def unlock():
            if password_entry.get() == APP_PASSWORD:
                self.lock_screen.destroy()
                self.lock_screen = None
                self.reset_session_timer()
            else:
                messagebox.showerror("Access Denied", "Incorrect Password")
                password_entry.delete(0, "end")

        # Unlock button
        ctk.CTkButton(
            self.lock_screen,
            text="Unlock",
            width=200,
            height=50,
            font=("Helvetica", 22, "bold"),
            command=unlock
        ).grid(row=3, column=0, pady=20)

        password_entry.bind("<Return>", lambda e: unlock())
        password_entry.focus_set()

    # -----------------------------
    # FRAME CONTROL
    # -----------------------------
    def show_frame(self, frame_name: str):
        frame = self.frames[frame_name]
        frame.tkraise()

        if hasattr(frame, "on_show"):
            frame.on_show()

    # -----------------------------
    # BACKEND UPDATE
    # -----------------------------
    def run_backend_update(self, reason="manual"):
        print(f"[APP] run_backend_update called. reason={reason}, mode={self.current_mode}")

        try:
            if self.current_mode == "Weather Mode":
                run_full_backend_update(
                    control_mode="Weather Mode",
                    weather_data=self.weather,
                    reason=reason
                )
            else:
                run_full_backend_update(
                    control_mode="User Mode",
                    selected_scale=self.selected_scale,
                    selected_key=self.selected_key,
                    reason=reason
                )

            print("Backend update complete.")

            import json
            with open("data/final_notes.json", "r") as f:
                notes = json.load(f)
                print("FINAL NOTES:", notes)

        except Exception as e:
            print("Backend update error:", e)

    # -----------------------------
    # MODE / USER SETTINGS
    # -----------------------------
    def set_mode(self, mode):
        print(f"[APP] set_mode called with mode={mode}")
        self.current_mode = mode
        self.run_backend_update(reason="mode changed")

    def set_user_selection(self, scale, key=None):
        print(f"[APP] set_user_selection called with scale={scale}, key={key}")
        self.selected_scale = scale
        self.selected_key = key
        self.run_backend_update(reason="user selection changed")

    # -----------------------------
    # WEATHER UPDATE LOOP
    # -----------------------------
    def update_weather(self):
        if self.update_running:
            print("[APP] Skipping update — already running")
            return

        print("[APP] update_weather start")

        def task():
            self.update_running = True

            try:
                from chime_update import chime_update
                chime_update(self)
                print("[APP] Weather + backend updated")

            except Exception as e:
                print("[APP] Update error:", e)

            finally:
                self.update_running = False

        threading.Thread(target=task, daemon=True).start()

        # Repeat every ~5 minutes
        self.after(500 * 60 * 10, self.update_weather)


# -----------------------------
# LOGIN WINDOW
# -----------------------------
class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("500x300")
        self.title("Windchimes Login")
        self.attributes("-fullscreen", True)

        self.grid_rowconfigure((0, 1, 2, 3), weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Title
        ctk.CTkLabel(
            self,
            text="Windchimes Access",
            font=("Helvetica", 36, "bold")
        ).grid(row=0, column=0, pady=(60, 20))

        # Password Entry
        self.password_entry = ctk.CTkEntry(
            self,
            show="*",
            width=300,
            height=50,
            font=("Helvetica", 22),
            placeholder_text="Enter Password"
        )
        self.password_entry.grid(row=1, column=0, pady=20)

        self.password_entry.bind("<Return>", lambda e: self.check_password())

        # Login Button
        ctk.CTkButton(
            self,
            text="Login",
            width=200,
            height=50,
            font=("Helvetica", 22, "bold"),
            command=self.check_password
        ).grid(row=2, column=0, pady=20)

        # Escape closes
        self.bind("<Escape>", lambda e: self.destroy())

    def check_password(self):
        if self.password_entry.get() == APP_PASSWORD:
            self.destroy()

            app = App()
            app.mainloop()

        else:
            messagebox.showerror(
                "Access Denied",
                "Incorrect Password"
            )

            self.password_entry.delete(0, "end")


# -----------------------------
# PROGRAM START
# -----------------------------
if __name__ == "__main__":
    print(APP_PASSWORD)
    login = LoginWindow()
    login.mainloop()
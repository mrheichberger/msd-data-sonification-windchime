import sys
import os
import signal
import customtkinter as ctk
import threading
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
APP_PASSWORD = os.getenv("PASSWORD")
SESSION_TIMEOUT = 15 * 60 * 1000  # 15 minutes


# -----------------------------
# HARD KILL FUNCTION
# -----------------------------
def kill_program():
    """Completely terminate entire Python process."""
    os._exit(0)


# Block terminal Ctrl+C from bypassing security
signal.signal(signal.SIGINT, lambda sig, frame: None)


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
        # SECURITY
        # -----------------------------
        self.protocol("WM_DELETE_WINDOW", lambda: None)

        # Escape is the ONLY intentional full shutdown
        self.bind("<Escape>", lambda e: kill_program())

        # Block common bypasses
        self.bind("<Control-c>", lambda e: "break")
        self.bind("<Control-C>", lambda e: "break")
        self.bind("<Alt-F4>", lambda e: "break")

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
        # WEATHER
        # -----------------------------
        self.weather_service = WeatherService()

        if self.weather_service.enabled:
            self.after(100, self.update_weather)

        # -----------------------------
        # FRAMES
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

        # -----------------------------
        # SESSION TIMER
        # -----------------------------
        self.reset_session_timer()

        self.bind_all("<KeyPress>", self.on_user_activity)
        self.bind_all("<Any-Button>", self.on_user_activity)

    # -----------------------------
    # USER ACTIVITY
    # -----------------------------
    def on_user_activity(self, event=None):
        self.reset_session_timer()
        return None

    # -----------------------------
    # SESSION TIMER
    # -----------------------------
    def reset_session_timer(self, event=None):
        if self.lock_screen:
            return

        if self.session_timer:
            self.after_cancel(self.session_timer)

        self.session_timer = self.after(
            SESSION_TIMEOUT,
            self.force_relogin
        )

    # -----------------------------
    # LOCK SCREEN
    # -----------------------------
    def force_relogin(self):
        if self.lock_screen:
            return

        self.lock_screen = ctk.CTkToplevel(self)
        self.lock_screen.attributes("-fullscreen", True)
        self.lock_screen.attributes("-topmost", True)
        self.lock_screen.title("Session Locked")

        # Make lock truly modal
        self.lock_screen.grab_set()
        self.lock_screen.focus_force()

        # Prevent closure
        self.lock_screen.protocol("WM_DELETE_WINDOW", lambda: None)

        # Block shortcuts
        self.lock_screen.bind("<Control-c>", lambda e: "break")
        self.lock_screen.bind("<Control-C>", lambda e: "break")
        self.lock_screen.bind("<Alt-F4>", lambda e: "break")
        self.lock_screen.bind("<Escape>", lambda e: "break")

        self.lock_screen.grid_rowconfigure((0, 1, 2, 3), weight=1)
        self.lock_screen.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            self.lock_screen,
            text="Session Locked",
            font=("Helvetica", 40, "bold")
        ).grid(row=0, column=0, pady=(80, 20))

        ctk.CTkLabel(
            self.lock_screen,
            text="Enter password to continue",
            font=("Helvetica", 22)
        ).grid(row=1, column=0)

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
                self.lock_screen.grab_release()
                self.lock_screen.destroy()
                self.lock_screen = None
                self.reset_session_timer()
            else:
                messagebox.showerror("Access Denied", "Incorrect Password")
                password_entry.delete(0, "end")

        ctk.CTkButton(
            self.lock_screen,
            text="Unlock",
            width=200,
            height=50,
            font=("Helvetica", 22, "bold"),
            command=unlock
        ).grid(row=3, column=0, pady=20)

        password_entry.bind("<Return>", lambda e: unlock())
        password_entry.focus_force()

    # -----------------------------
    # FRAME CONTROL
    # -----------------------------
    def show_frame(self, frame_name):
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
    # USER SETTINGS
    # -----------------------------
    def set_mode(self, mode):
        self.current_mode = mode
        self.run_backend_update(reason="mode changed")

    def set_user_selection(self, scale, key=None):
        self.selected_scale = scale
        self.selected_key = key
        self.run_backend_update(reason="user selection changed")

    # -----------------------------
    # WEATHER LOOP
    # -----------------------------
    def update_weather(self):
        if self.update_running:
            return

        def task():
            self.update_running = True

            try:
                from chime_update import chime_update
                chime_update(self)

            except Exception as e:
                print("[APP] Update error:", e)

            finally:
                self.update_running = False

        threading.Thread(target=task, daemon=True).start()

        self.after(500 * 60 * 10, self.update_weather)


# -----------------------------
# REPLACE YOUR LoginWindow CLASS WITH THIS VERSION
# -----------------------------
class LoginWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.geometry("800x600")
        self.title("Windchimes Login")
        self.attributes("-fullscreen", True)

        # Security
        self.protocol("WM_DELETE_WINDOW", lambda: None)

        # Escape fully exits
        self.bind("<Escape>", lambda e: kill_program())

        # Block bypasses
        self.bind("<Control-c>", lambda e: "break")
        self.bind("<Control-C>", lambda e: "break")
        self.bind("<Alt-F4>", lambda e: "break")

        # Layout
        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)
        self.grid_columnconfigure(0, weight=1)

        # -----------------------------
        # TITLE
        # -----------------------------
        ctk.CTkLabel(
            self,
            text="Windchimes Access",
            font=("Helvetica", 42, "bold")
        ).grid(row=0, column=0, pady=(40, 10))

        # -----------------------------
        # PASSWORD ENTRY
        # -----------------------------
        self.password_entry = ctk.CTkEntry(
            self,
            show="*",
            width=350,
            height=60,
            font=("Helvetica", 28),
            justify="center",
            placeholder_text="Enter PIN"
        )
        self.password_entry.grid(row=1, column=0, pady=10)

        self.password_entry.bind("<Return>", lambda e: self.check_password())

        # -----------------------------
        # KEYPAD FRAME
        # -----------------------------
        keypad_frame = ctk.CTkFrame(self, fg_color="transparent")
        keypad_frame.grid(row=2, column=0, pady=20)

        # Configure keypad grid
        for r in range(4):
            keypad_frame.grid_rowconfigure(r, weight=1)

        for c in range(3):
            keypad_frame.grid_columnconfigure(c, weight=1)

        # Button layout
        buttons = [
            "1", "2", "3",
            "4", "5", "6",
            "7", "8", "9",
            "Clear", "0", "⌫"
        ]

        # Create smaller buttons
        row = 0
        col = 0

        for btn in buttons:
            ctk.CTkButton(
                keypad_frame,
                text=btn,
                width=70,          # Smaller width
                height=40,         # Smaller height
                corner_radius=12,
                font=("Helvetica", 16, "bold"),
                command=lambda value=btn: self.keypad_press(value)
            ).grid(
                row=row,
                column=col,
                padx=6,
                pady=6
            )

            col += 1
            if col > 2:
                col = 0
                row += 1

        # -----------------------------
        # LOGIN BUTTON
        # -----------------------------
        ctk.CTkButton(
            self,
            text="Login",
            width=250,
            height=65,
            font=("Helvetica", 28, "bold"),
            command=self.check_password
        ).grid(row=3, column=0, pady=20)

        self.password_entry.focus_force()

    # -----------------------------
    # KEYPAD INPUT
    # -----------------------------
    def keypad_press(self, value):
        current = self.password_entry.get()

        if value == "Clear":
            self.password_entry.delete(0, "end")

        elif value == "⌫":
            if len(current) > 0:
                self.password_entry.delete(len(current) - 1, "end")

        else:
            self.password_entry.insert("end", value)

    # -----------------------------
    # PASSWORD CHECK
    # -----------------------------
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
# START PROGRAM
# -----------------------------
if __name__ == "__main__":
    login = LoginWindow()
    login.mainloop()
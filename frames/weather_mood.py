import customtkinter as ctk
import json

class WeatherMoodFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master)
        self.controller = controller
        
    
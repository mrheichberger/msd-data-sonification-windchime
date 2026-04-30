import customtkinter as ctk
from PIL import Image
import requests
from io import BytesIO


class MonitorFrame(ctk.CTkFrame):
    def __init__(self, master, controller):
        super().__init__(master, corner_radius=15)
        self.controller = controller

        self.icon_img = None

        # ===== MAIN LAYOUT (GRID FIX) =====
        self.grid_rowconfigure(0, weight=1)  # content grows
        self.grid_rowconfigure(1, weight=0)  # footer fixed
        self.grid_columnconfigure(0, weight=1)

        # ===== CONTENT =====
        self.content = ctk.CTkFrame(self)
        self.content.grid(row=0, column=0, sticky="nsew")

        self.content.grid_rowconfigure(1, weight=1)
        self.content.grid_columnconfigure(0, weight=1)

        # ===== TITLE =====
        ctk.CTkLabel(
            self.content,
            text="Weather Monitor",
            font=("Helvetica", 20, "bold")
        ).grid(row=0, column=0, pady=(15, 5))

        # ===== MAIN CARD =====
        self.card = ctk.CTkFrame(self.content, corner_radius=12)
        self.card.grid(row=1, column=0, padx=20, pady=5, sticky="nsew")

        # ===== TOP ROW (FIXED: ONE LINE) =====
        self.top_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.top_frame.pack(pady=10, fill="x")

        self.top_inner = ctk.CTkFrame(self.top_frame, fg_color="transparent")
        self.top_inner.pack(anchor="center")

        self.icon_label = ctk.CTkLabel(self.top_inner, text="")
        self.icon_label.pack(side="left", padx=15)

        self.temp_label = ctk.CTkLabel(
            self.top_inner,
            text="--°F",
            font=("Helvetica", 32, "bold")
        )
        self.temp_label.pack(side="left", padx=15)

        # ===== TILES =====
        self.tiles_frame = ctk.CTkFrame(self.card, fg_color="transparent")
        self.tiles_frame.pack(pady=7, fill="both", expand=True)

        for i in range(3):
            self.tiles_frame.grid_columnconfigure(i, weight=1)

        self.tiles = {
            "Condition": self.create_tile("Condition"),
            "Wind": self.create_tile("Wind"),
            "Humidity": self.create_tile("Humidity"),
            "Clouds": self.create_tile("Clouds"),
            "Rain": self.create_tile("Chance of Rain"),
            "AQI": self.create_tile("AQI"),
        }

        keys = list(self.tiles.keys())
        for i, key in enumerate(keys):
            self.tiles[key].grid(
                row=i // 3,
                column=i % 3,
                padx=10,
                pady=10,
                sticky="nsew"
            )

        # ===== FOOTER (NOW GUARANTEED VISIBLE) =====
        self.footer = ctk.CTkFrame(self, fg_color="transparent")
        self.footer.grid(row=1, column=0, sticky="ew", pady=10)

        self.home_btn = ctk.CTkButton(
            self.footer,
            text="Go Home",
            height=40,
            command=lambda: controller.show_frame("HomeFrame")
        )
        self.home_btn.pack()

    # ===== TILE CREATOR =====
    def create_tile(self, title):
        return ctk.CTkButton(
            self.tiles_frame,
            text=f"{title}\n--",
            font=("Helvetica", 16),
            height=90,
            corner_radius=12,
            fg_color="#2b2b2b",
            hover_color="#3a3a3a"
        )

    # ===== LOAD ICON =====
    def load_icon(self, url, size=(140, 140)):
        try:
            response = requests.get(url, timeout=5)
            img = Image.open(BytesIO(response.content)).resize(size)
            return ctk.CTkImage(light_image=img, dark_image=img, size=size)
        except:
            return None

    # ===== UPDATE DISPLAY =====
    def on_show(self):
        weather = self.controller.weather
        if not weather:
            return

        current = weather["current"]
        extra = weather["extra"]

        # ===== MAIN ROW =====
        self.temp_label.configure(text=f"{current['temp']}°F")
    
        # ===== ICON =====
        icon_url = current["weather"][0].get("icon")
        if icon_url:
            icon_img = self.load_icon(icon_url)
            if icon_img:
                self.icon_label.configure(image=icon_img, text="")
                self.icon_label.image = icon_img

        # ===== TILES =====
        self.tiles["Condition"].configure(
            text=f"Condition\n{current['weather'][0]['main']}"
        )
        self.tiles["Wind"].configure(
            text=f"Wind\n{extra['wind_speed']} mph"
        )
        self.tiles["Humidity"].configure(
            text=f"Humidity\n{extra['humidity']}%"
        )
        self.tiles["Clouds"].configure(
            text=f"Clouds\n{extra['clouds']}%"
        )
        self.tiles["Rain"].configure(
            text=f"Chance of Rain\n{extra['pop']:.0f}%"
        )
        self.tiles["AQI"].configure(
            text=f"AQI\n{extra['aqi']}"
        )
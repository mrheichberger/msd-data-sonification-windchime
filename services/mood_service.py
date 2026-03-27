from client import Mood


class MoodService:
    def calculate_mood(self, weather):
        mood_points = {m: 0 for m in Mood}

        temp = weather.get("temp", 0)

        if 65 <= temp <= 85:
            mood_points[Mood.JOYOUS] += 1
        if 40 <= temp <= 60:
            mood_points[Mood.MELANCHOLY] += 1

        return max(mood_points, key=mood_points.get)
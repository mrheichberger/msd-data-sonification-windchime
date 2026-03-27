import os
import json


def generate_lines():
    #BASE_PATH = os.path.dirname(os.path.abspath(__file__))
    
    TTS_ROOT = r".\tts"
    JSON_PATH = os.path.join(TTS_ROOT, "tts_lines.json")
    
    if not os.path.exists(JSON_PATH):
        print(f"Error: {JSON_PATH} not found.")
        return
    
    with open(JSON_PATH, 'r') as file:
        lines = json.load(file)

    for page in lines:
        for line in lines[page]:
            filename = os.path.join(TTS_ROOT, page, f"{line}.wav")
            os.makedirs(os.path.dirname(filename), exist_ok=True)

            if not os.path.exists(filename):
                os.system(f'espeak "{lines[page][line]}" -w {filename}')
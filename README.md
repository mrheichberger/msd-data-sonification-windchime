# MSD Data Sonification Windchime

## Overview

This project is a data-driven windchime system that converts either user-selected musical settings or live weather conditions into physical chime configurations.

The Python backend is responsible for:

- Selecting the active musical scale and key  
- Updating the active note-state JSON  
- Mapping note states to Geneva mechanism target positions  
- Calculating how far each chime set must rotate  
- Sending motor movement commands over UART from the Raspberry Pi to the Raspberry Pi Pico  
- Storing the current physical position of each chime set  

The system supports two control modes:

- **User Mode**: The user selects a scale/key or uses a scheduled timetable entry  
- **Weather Mode**: Live weather data from the API is mapped to a scale/key pair  

---

## Repository Structure

```text
.
├── app.py
├── main_backend.py
├── scale_manager.py
├── chime_mapper.py
├── current_chime_position.py
├── uart_service.py
├── weather_mode_mapper.py
├── time_helper.py
├── test_full_pipeline.py
├── test_weather_mapper.py
├── timetable_configs.json
├── current_chime_position.json
├── README.md
├── data/
│   ├── chime_states.json
│   ├── final_notes.json
│   └── weather_mood_config.json
├── frames/
├── services/
└── motor_control_program/
---
```
## Backend Flow

1. Determine whether the system is in user mode or weather mode  
2. Select the active scale and key  
3. Update `final_notes.json` with the active note state  
4. Map note states to 8 Geneva target positions  
5. Read the current physical chime positions from `current_chime_position.json`  
6. Calculate how many slots each chime set needs to rotate  
7. Send movement commands over UART to the Pico  
8. Read back the actual movement from the Pico  
9. Update `current_chime_position.json`  

---

## main_backend.py

### Overview

Main backend control module that determines control mode and updates the active note state.

### Responsibilities

- Loads the scale manager  
- Loads the chime mapper  
- Loads the weather mode mapper  
- Checks for an active scheduled scale entry  
- Updates `data/final_notes.json`  
- Returns target Geneva positions  

### Behavior

#### Weather Mode

- Requires `weather_data`  
- Uses `WeatherModeMapper`  
- Retrieves a scale and key  
- Updates note state via `ScaleManager`  

#### User Mode

- Checks `timetable_configs.json` first  
- Uses scheduled entry if active  
- Otherwise uses GUI selection  
- Supports `"Custom"` scales  

---

## scale_manager.py

### Overview

Handles scale selection and writes the active note state.

### Responsibilities

- Read from `data/chime_states.json`  
- Update `data/final_notes.json`  
- Handle keyed scales  
- Handle custom note selections  

---

## chime_mapper.py

### Overview

Maps note states to Geneva mechanism positions.

### Responsibilities

- Read `final_notes.json`  
- Group notes into 8 mechanical pairs  
- Convert note states into target positions  

### Note Pairs

- (C4, C#4)  
- (D4, D#4)  
- (E4, F4)  
- (F#4, G4)  
- (G#4, A4)  
- (A#4, B4)  
- (C5, C#5)  
- (D5, D#5)  

### Important

This module returns **target positions only**.  
It does **not** calculate motor movement.

---

## current_chime_position.py

### Overview

Tracks and updates physical chime positions.

### Responsibilities

- Read `current_chime_position.json`  
- Compare current vs target positions  
- Calculate required movement  
- Send UART commands  
- Read actual movement  
- Update saved positions  

---

## uart_service.py

### Overview

Handles UART communication between Raspberry Pi and Pico.

### Responsibilities

- Connect to `/dev/serial0`  
- Send motor commands  
- Receive movement feedback  

```markdown
### Protocol

**Pi → Pico**
motor_number
slots

**Pico -> Pi**
actual_slots_moved 
```
---

## weather_mode_mapper.py

### Overview

Maps weather API data to a scale and key.

### Responsibilities

- Parse OpenWeather API data  
- Classify weather condition  
- Bucket temperature ranges  
- Generate lookup keys  
- Return scale and key  

### Notes

- Uses configurable mappings  
- Falls back to `Major / C` if needed  
- Only selects scale/key (not notes)  

---

## JSON Files

### `data/chime_states.json`
Stores available scale definitions.

### `data/final_notes.json`
Stores the currently active note state.

### `current_chime_position.json`
Stores current Geneva positions for each chime set.

### `timetable_configs.json`
Stores scheduled scale selections.

---

## System Summary

The backend converts musical intent into physical motion:

Input (GUI / Weather)
↓
Scale Selection
↓
final_notes.json
↓
Chime Mapping
↓
Target Positions
↓
Compare with Current Positions
↓
UART → Pico
↓
Motor Movement
↓
Update Saved State

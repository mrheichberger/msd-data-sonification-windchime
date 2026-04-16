from main_backend import update_final_json
import json
from chime_mapper import ChimeMapper
from uart_service import UARTComm

CURRENT_POSITIONS_PATH = "current_chime_position.json"
FINAL_PATH = "data/final_notes.json"


def load_current_positions():
    with open(CURRENT_POSITIONS_PATH, "r") as f:
        return json.load(f)


def save_current_positions(positions):
    with open(CURRENT_POSITIONS_PATH, "w") as f:
        json.dump(positions, f, indent=4)


def get_target_positions():
    mapper = ChimeMapper(FINAL_PATH)
    target_list = mapper.map_final_notes_to_positions()

    target_dict = {}
    for i, pos in enumerate(target_list, start=1):
        target_dict[f"set_{i}"] = pos

    return target_dict


def compute_uart_commands(current_positions, target_positions):
    commands = {}

    for key in current_positions:
        current = current_positions[key]
        target = target_positions[key]
        slots_to_move = (target - current) % 6
        commands[key] = slots_to_move

    return commands


def apply_uart_moves():
    current_positions = load_current_positions()
    target_positions = get_target_positions()
    uart_commands = compute_uart_commands(current_positions, target_positions)

    uart = UARTComm()
    uart.connect()

    try:
        for i in range(1, 9):
            key = f"set_{i}"
            slots_to_move = uart_commands[key]

            if slots_to_move != 0:
                actual_slots_moved = uart.move_motor_and_get_result(i, slots_to_move)

                current = current_positions[key]
                new_pos = ((current - 1 + actual_slots_moved) % 6) + 1
                current_positions[key] = new_pos

        save_current_positions(current_positions)

    finally:
        uart.close()


def run_full_backend_update(control_mode, weather_data=None, selected_scale=None, selected_key=None):
    update_final_json(
        control_mode=control_mode,
        weather_data=weather_data,
        selected_scale=selected_scale,
        selected_key=selected_key
    )
    apply_uart_moves()


    '''
    This module is responsible for converting musical state into physical motion.

Overall flow:

1. Read CURRENT positions
   - Load current_chime_position.json
   - This represents where each Geneva mechanism is physically right now (1–6)

2. Compute TARGET positions
   - Use ChimeMapper to convert final_notes.json → target positions
   - These are the desired Geneva positions for each set

3. Calculate MOVEMENT required
   - For each set:
        slots_to_move = (target - current) % 6
   - This determines how many forward steps the motor must rotate

4. Send commands over UART
   - For each set that needs movement:
        send (motor_number, slots_to_move)
   - motor_number = 1–8 corresponding to each chime set

5. Read actual movement from Pico
   - Pico returns how many slots it actually moved
   - This accounts for real-world behavior (missed steps, etc.)

6. Update CURRENT positions
   - new_position = ((current - 1 + actual_slots_moved) % 6) + 1
   - This keeps positions wrapped in range 1–6

7. Save updated state
   - Write updated positions back to current_chime_position.json
   - This ensures next cycle starts from correct physical state

------------------------------------------------------------

Key Concepts:

- TARGET position = where the system wants to go (from music logic)
- CURRENT position = where hardware actually is (stored in JSON)
- SLOTS TO MOVE = difference between target and current

- UART is only responsible for:
    sending motor commands
    receiving actual movement feedback

- This file acts as the "bridge" between:
    software (notes, scales, weather)
    and hardware (motors, encoders)

------------------------------------------------------------

Example:

Current:
    set_1 = 1

Target:
    set_1 = 3

Movement:
    (3 - 1) % 6 = 2 → rotate forward 2 slots

After movement:
    new_position = 3 (saved to JSON)

------------------------------------------------------------'''
from main_backend import update_final_json
import json
import time
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


def load_final_notes_snapshot():
    try:
        with open(FINAL_PATH, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def get_target_positions():
    mapper = ChimeMapper(FINAL_PATH)
    target_list = mapper.map_final_notes_to_positions()

    target_dict = {}
    for i, pos in enumerate(target_list, start=1):
        target_dict[f"set_{i}"] = pos

    return target_dict


def positions_need_update():
    """
    Returns True when any set's current position differs from the mapped target.
    """
    current_positions = load_current_positions()
    target_positions = get_target_positions()

    for key, current in current_positions.items():
        if target_positions.get(key) != current:
            return True
    return False

def compute_uart_commands(current_positions, target_positions):
    commands = {}

    for key in current_positions:
        current = current_positions[key]
        target = target_positions[key]
        slots_to_move = (target - current) % 6
        commands[key] = slots_to_move

    return commands

def apply_uart_moves():
    print("[UART] Preparing UART move application")
    current_positions = load_current_positions()
    target_positions = get_target_positions()
    uart_commands = compute_uart_commands(current_positions, target_positions)
    print(f"[UART] Current positions: {current_positions}")
    print(f"[UART] Target positions: {target_positions}")
    print(f"[UART] Computed commands: {uart_commands}")

    uart = UARTComm()
    uart.connect()

    try:
        uart.send_clear_command()
        for i in range(1, 9):
            key = f"set_{i}"
            slots_to_move = uart_commands[key]

            if slots_to_move != 0:
                try:
                    started_at = time.time()
                    print(
                        f"[UART] {key}: command start motor={i}, requested_slots={slots_to_move}"
                    )
                    actual_slots_moved = uart.move_motor_and_get_result(i, slots_to_move)
                    elapsed = time.time() - started_at
                    print(
                        f"[UART] {key}: response received in {elapsed:.2f}s, actual_slots={actual_slots_moved}"
                    )

                    # 🔍 Check mismatch
                    if actual_slots_moved != slots_to_move:
                        print(
                            f"[MISMATCH] {key}: expected {slots_to_move}, got {actual_slots_moved}"
                        )
                    else:
                        print(
                            f"[OK] {key}: moved {actual_slots_moved} slots"
                        )

                except Exception as e:
                    print(
                        f"[UART FAIL] {key}: expected {slots_to_move}, no valid response in timeout. Using expected fallback. Error: {e}"
                    )
                    actual_slots_moved = slots_to_move

                # Update position from actual UART feedback or expected fallback
                current = current_positions[key]
                new_pos = ((current - 1 + actual_slots_moved) % 6) + 1
                current_positions[key] = new_pos
            else:
                print(f"[UART] {key}: already aligned, skipping")

        save_current_positions(current_positions)
        print(f"[UART] Saved updated positions: {current_positions}")

    finally:
        uart.close()
        print("[UART] UART connection closed")


def run_full_backend_update(control_mode, weather_data=None, selected_scale=None, selected_key=None, reason="unspecified"):
    print(f"[RUN_FULL_BACKEND_UPDATE] reason={reason}")
    print(f"[RUN_FULL_BACKEND_UPDATE] control_mode={control_mode}")
    print(f"[RUN_FULL_BACKEND_UPDATE] selected_scale={selected_scale}, selected_key={selected_key}")
    print(f"[RUN_FULL_BACKEND_UPDATE] weather_data_present={weather_data is not None}")

    before_notes = load_final_notes_snapshot()
    print(f"[RUN_FULL_BACKEND_UPDATE] final_notes before update: {before_notes}")

    update_final_json(
        control_mode=control_mode,
        weather_data=weather_data,
        selected_scale=selected_scale,
        selected_key=selected_key
    )
    after_notes = load_final_notes_snapshot()
    print(f"[RUN_FULL_BACKEND_UPDATE] final_notes after update: {after_notes}")

    final_notes_changed = before_notes != after_notes
    print(f"[RUN_FULL_BACKEND_UPDATE] final_notes_changed={final_notes_changed}")
    positions_changed = positions_need_update()
    print(f"[RUN_FULL_BACKEND_UPDATE] positions_need_update={positions_changed}")

    if final_notes_changed or positions_changed:
        if final_notes_changed and positions_changed:
            print("[RUN_FULL_BACKEND_UPDATE] notes changed and positions differ, applying UART moves")
        elif final_notes_changed:
            print("[RUN_FULL_BACKEND_UPDATE] final_notes changed, applying UART moves")
        else:
            print("[RUN_FULL_BACKEND_UPDATE] final_notes unchanged but positions differ, applying UART moves")
        apply_uart_moves()
        print("[RUN_FULL_BACKEND_UPDATE] UART moves applied")
    else:
        print("[RUN_FULL_BACKEND_UPDATE] final_notes unchanged and positions already aligned, skipping UART")
    


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
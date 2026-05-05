# MSD Data Sonification Windchime

Data-driven windchime system that maps musical note selections (user mode) or weather-driven mappings (weather mode) into physical Geneva-slot motor positions.

## What This Project Does

- Selects a scale/key from user input, timetable, or weather mapping.
- Writes active notes into `data/final_notes.json`.
- Maps notes to target Geneva positions for 8 chime sets.
- Compares target positions to `current_chime_position.json`.
- Sends UART motor commands from Raspberry Pi to Pico.
- Reads back actual moved slots from the Pico.
- Updates saved current positions.

## Main Components

- `app.py`: app/runtime orchestration.
- `main_backend.py`: mode selection and end-to-end backend update logic.
- `scale_manager.py`: applies selected scale/key into active notes.
- `chime_mapper.py`: converts note-state to 8 target set positions.
- `current_chime_position.py`: computes required moves and applies UART updates.
- `uart_service.py`: Pi-side UART transport and response parsing.
- `weather_mode_mapper.py`: maps weather conditions to scale/key.
- `motor_control_program/`: Pico firmware for UART command parsing and motor execution.

## Control Modes

- `User Mode`: GUI selection or active timetable config controls scale/key.
- `Weather Mode`: weather API condition/temperature selects scale/key.

## Runtime Flow

1. Determine active mode.
2. Resolve scale/key.
3. Update `data/final_notes.json`.
4. Map notes to target positions.
5. Compare with `current_chime_position.json`.
6. Send per-motor UART command (`motor`, `slots`).
7. Receive actual slots moved from Pico.
8. Persist updated positions.

## UART Protocol

### Standard Move Command

Pi sends two newline-delimited integers:

1. `motor_number` (1-8)
2. `requested_slots` (>0)

Pico returns one newline-delimited integer:

- `actual_slots_moved`

### Special Commands / Error Codes

- `c` (Pi -> Pico): clear command queue + parser state.
- `0` (Pico -> Pi): clear acknowledged.
- `-77` (Pico -> Pi): invalid token/protocol parse error.
- `-88` (Pico -> Pi): command queue full.

## Pico Motor Control Behavior (Current)

The firmware is encoder-informed slot control (not PID):

- Move command is treated as relative movement: "move N slots from current position."
- Loop tracks moved slots via encoder (`current_slot - start_slot`).
- Stops when moved slots reach requested slots.
- Includes guard timeouts:
  - `MOVE_TIMEOUT_MS` (overall move timeout)
  - `FIRST_EDGE_TIMEOUT_MS` (max wait before first encoder motion)
  - `NO_MOTION_TIMEOUT_MS` (max no-motion gap after movement starts)
- Includes post-stop settle window:
  - `SETTLE_TIME_MS`, `SETTLE_TIMEOUT_MS`
- Slowdown near target is currently disabled for no-load testing:
  - `SLOWDOWN_SLOTS = 0`

## Position Data Files

- `data/chime_states.json`: scale definitions.
- `data/final_notes.json`: active note-state.
- `current_chime_position.json`: last known physical set positions.
- `timetable_configs.json`: scheduled user mode selections.

## Build / Flash (Pico Firmware)

From project root:

```bash
cd motor_control_program
cd build
ninja
```

Flash the produced UF2/firmware artifact to the Pico using your normal process.

## Validation Checklist

After flashing:

1. Send small moves (`1`, `2`, `4`) on a couple motors.
2. Confirm Pico returns plausible `actual_slots_moved`.
3. Run one full backend update and confirm mismatch rate is low.
4. Watch for protocol errors (`-77`, `-88`) and investigate if seen.

## Tuning Notes

If results are consistently short or noisy, tune in this order:

1. `SLOWDOWN_SLOTS` / near-target speed (only if needed under load).
2. `FIRST_EDGE_TIMEOUT_MS` (if startup is slow).
3. `NO_MOTION_TIMEOUT_MS` (if moves pause mid-travel).
4. `SETTLE_TIME_MS` (if response is sent before mechanics fully settle).

## Troubleshooting

### Pattern: Every command returns `0` quickly

Example:
- requested: `4`, actual: `0`
- similar response time each command

Likely causes:
- no encoder motion detected
- first-edge timeout/no-motion timeout too aggressive
- encoder wiring/noise/power issue

What to do:
1. Increase `FIRST_EDGE_TIMEOUT_MS` (startup allowance).
2. Verify encoder counts change while motor is physically moving.
3. Check encoder pin mapping and pull-ups.

### Pattern: Almost all commands return `N-1` (one short)

Example:
- requested: `4`, actual: `3`
- requested: `2`, actual: `1`

Likely causes:
- slowdown near target is too aggressive
- mechanism stalls in final slot region

What to do:
1. Set `SLOWDOWN_SLOTS = 0` for no-load tests.
2. If running under load, increase near-target speed or reduce slowdown window.
3. Increase `NO_MOTION_TIMEOUT_MS` slightly if final slot is slow.

### Pattern: Random negative return values (for example `-19`)

Likely causes:
- encoder direction reversal/noise/glitch during move
- unstable signal integrity on one channel

What to do:
1. Inspect encoder channel wiring for that motor.
2. Compare raw encoder counts while commanding a single known move.
3. In backend, reject impossible values (`actual < 0` or far above expected) and retry.

### Pattern: Frequent `-77` responses

Meaning:
- Pico rejected malformed UART token.

What to do:
1. Ensure Pi sends exactly newline-delimited integer tokens.
2. Call clear (`c`) to resync parser/queue state.
3. Check for mixed debug text accidentally written to UART.

### Pattern: Frequent `-88` responses

Meaning:
- Pico command queue is full.

What to do:
1. Reduce burst rate of command sends.
2. Wait for command completion before issuing more moves.
3. Retry after current queue drains.

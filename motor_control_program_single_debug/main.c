#include "../motor_control_program/motor_driver.h"
#include "../motor_control_program/encoder.h"
#include "../motor_control_program/uart_comm.h"
#include <pico/stdlib.h>
#include <stdio.h>

#define TEST_MOTOR_NUM 1
#define GENEVA_SLOTS_PER_REV 6
#define ENCODER_DETENTS_PER_REV 24
#define ENCODER_COUNTS_PER_DETENT 4
#define ENCODER_COUNTS_PER_REV (ENCODER_DETENTS_PER_REV * ENCODER_COUNTS_PER_DETENT)
#define COUNTS_PER_SLOT (ENCODER_COUNTS_PER_REV / GENEVA_SLOTS_PER_REV)
#define SLOT_THRESHOLD_COUNTS 3
#define MOVE_TIMEOUT_MS 30000

static int32_t move_geneva_slots_debug(motor_driver_t *m, encoder_t *enc, int32_t requested_slots) {
    if (requested_slots <= 0) {
        printf("[DBG] requested_slots <= 0, skipping\n");
        return 0;
    }

    int32_t start_counts = encoder_get_position(enc);
    int32_t start_slot = encoder_get_slot(enc, COUNTS_PER_SLOT, SLOT_THRESHOLD_COUNTS);
    int32_t target_slot = start_slot + requested_slots;

    printf("[DBG] move start | req=%ld start_counts=%ld start_slot=%ld target_slot=%ld\n",
           (long)requested_slots, (long)start_counts, (long)start_slot, (long)target_slot);

    motor_forward_full(m);

    int timeout_ms = 0;
    while (1) {
        int32_t current_counts = encoder_get_position(enc);
        int32_t current_slot = encoder_get_slot(enc, COUNTS_PER_SLOT, SLOT_THRESHOLD_COUNTS);

        if (timeout_ms % 250 == 0) {
            printf("[DBG] loop t=%dms counts=%ld slot=%ld target=%ld\n",
                   timeout_ms, (long)current_counts, (long)current_slot, (long)target_slot);
        }

        if (current_slot >= target_slot) {
            printf("[DBG] target reached\n");
            break;
        }

        sleep_ms(1);
        timeout_ms++;

        if (timeout_ms > MOVE_TIMEOUT_MS) {
            printf("[DBG] TIMEOUT waiting for slot target\n");
            break;
        }
    }

    motor_stop(m);
    sleep_ms(10);

    int32_t end_counts = encoder_get_position(enc);
    int32_t end_slot = encoder_get_slot(enc, COUNTS_PER_SLOT, SLOT_THRESHOLD_COUNTS);
    int32_t actual_slots_moved = end_slot - start_slot;

    printf("[DBG] move end | end_counts=%ld end_slot=%ld actual_slots=%ld delta_counts=%ld\n",
           (long)end_counts, (long)end_slot, (long)actual_slots_moved, (long)(end_counts - start_counts));

    return actual_slots_moved;
}

int main() {
    stdio_init_all();
    sleep_ms(2000);

    printf("\n=== single motor encoder debug ===\n");
    printf("[DBG] motor=%d pwm_pin=0 enc_a=8 enc_b=9\n", TEST_MOTOR_NUM);
    printf("[DBG] counts_per_slot=%d threshold=%d timeout_ms=%d\n",
           COUNTS_PER_SLOT, SLOT_THRESHOLD_COUNTS, MOVE_TIMEOUT_MS);
    printf("[DBG] send one integer slot command over UART (example: 2)\n");

    motor_driver_t motor = {
        .pwm_pin = 0,
        .wrap = 10000,
        .clkdiv = 4.0f
    };

    encoder_t encoder = {
        .pin_a = 8,
        .pin_b = 9,
        .use_pullups = true
    };

    motor_init(&motor);
    encoder_init(&encoder);
    uart_comm_init();

    int32_t requested_slots = 0;
    while (1) {
        if (uart_comm_read_int(&requested_slots)) {
            printf("[DBG] UART received slots=%ld\n", (long)requested_slots);
            int32_t actual_slots = move_geneva_slots_debug(&motor, &encoder, requested_slots);
            printf("[DBG] sending actual_slots=%ld\n", (long)actual_slots);
            uart_comm_send_int(actual_slots);
        }
        sleep_ms(5);
    }
}

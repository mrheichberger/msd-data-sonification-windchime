#include "../motor_control_program/motor_driver.h"
#include "../motor_control_program/encoder.h"
#include "../motor_control_program/uart_comm.h"
#include <pico/stdlib.h>
#include <stdio.h>

#define TEST_MOTOR_NUM 1
#define GENEVA_SLOTS_PER_REV 6
/* Quadrature counts per one Geneva slot (encoder_get_position / encoder_get_slot). Calibrate on hardware. */
#ifndef QUADRATURE_COUNTS_PER_GENEVA_SLOT
#define QUADRATURE_COUNTS_PER_GENEVA_SLOT 16
#endif
#define COUNTS_PER_SLOT QUADRATURE_COUNTS_PER_GENEVA_SLOT
#define SLOT_THRESHOLD_COUNTS 3
#define MOVE_TIMEOUT_MS 30000

static int32_t move_geneva_slots_debug(motor_driver_t *m, encoder_t *enc, int32_t requested_slots) {
    if (requested_slots <= 0) {
        printf("[DBG] requested_slots <= 0, skipping\n");
        return 0;
    }

    int32_t start_counts = encoder_get_position(enc);
    uint32_t start_edges = encoder_get_quad_edge_count(enc);
    int32_t start_slot = encoder_get_slot(enc, COUNTS_PER_SLOT, SLOT_THRESHOLD_COUNTS);
    int32_t target_slot = start_slot + requested_slots;

    printf("[DBG] move start | req=%ld pos=%ld quad_edges=%lu slot=%ld target_slot=%ld\n",
           (long)requested_slots, (long)start_counts, (unsigned long)start_edges,
           (long)start_slot, (long)target_slot);

    motor_forward_full(m);

    int timeout_ms = 0;
    while (1) {
        int32_t current_counts = encoder_get_position(enc);
        uint32_t current_edges = encoder_get_quad_edge_count(enc);
        int32_t current_slot = encoder_get_slot(enc, COUNTS_PER_SLOT, SLOT_THRESHOLD_COUNTS);

        if (timeout_ms % 250 == 0) {
            printf("[DBG] loop t=%dms pos=%ld quad_edges=%lu slot=%ld target=%ld\n",
                   timeout_ms, (long)current_counts, (unsigned long)current_edges,
                   (long)current_slot, (long)target_slot);
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
    uint32_t end_edges = encoder_get_quad_edge_count(enc);
    int32_t end_slot = encoder_get_slot(enc, COUNTS_PER_SLOT, SLOT_THRESHOLD_COUNTS);
    int32_t actual_slots_moved = end_slot - start_slot;
    uint32_t delta_edges = end_edges - start_edges;

    printf("[DBG] move end | pos=%ld quad_edges=%lu d_pos=%ld d_edges=%lu slot=%ld actual_slots=%ld\n",
           (long)end_counts, (unsigned long)end_edges,
           (long)(end_counts - start_counts), (unsigned long)delta_edges,
           (long)end_slot, (long)actual_slots_moved);
    printf("[DBG] cal hint: d_edges/d_pos should match if one-way; d_edges/slots ~= quad edges per Geneva slot\n");

    return actual_slots_moved;
}

int main() {
    stdio_init_all();
    sleep_ms(2000);

    printf("\n=== single motor encoder debug ===\n");
    printf("[DBG] motor=%d pwm_pin=0 enc_a=8 enc_b=9\n", TEST_MOTOR_NUM);
    printf("[DBG] geneva_slots=%d quad_counts/slot=%d threshold=%d timeout_ms=%d (QDEC integrated pos)\n",
           GENEVA_SLOTS_PER_REV, COUNTS_PER_SLOT, SLOT_THRESHOLD_COUNTS, MOVE_TIMEOUT_MS);
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

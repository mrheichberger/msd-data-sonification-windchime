#include "motor_driver.h"
#include "encoder.h"
#include <pico/stdlib.h>
#include <stdio.h>
#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include "uart_comm.h"

#define GENEVA_SLOTS_PER_REV 6

#ifndef QUADRATURE_COUNTS_PER_GENEVA_SLOT
#define QUADRATURE_COUNTS_PER_GENEVA_SLOT 16
#endif

#define COUNTS_PER_SLOT QUADRATURE_COUNTS_PER_GENEVA_SLOT
#define SLOT_THRESHOLD_COUNTS 0

// wait up to 1 full minute for movement before timing out
#define MOVE_TIMEOUT_MS 60000

#define UART_TOKEN_MAX_LEN 16


typedef enum {
    WAIT_FIRST_TOKEN,
    WAIT_A_MOTOR,
    WAIT_SLOT_COUNT
} uart_state_t;


// Reads UART characters until newline, then returns one complete token.
// Example tokens: "a", "3", "2"
bool uart_read_token(char *out, int max_len)
{
    static char buffer[UART_TOKEN_MAX_LEN];
    static int index = 0;

    char c;

    while (uart_comm_read_char(&c)) {

        if (c == '\r') {
            continue;
        }

        if (c == '\n') {
            if (index == 0) {
                continue;
            }

            buffer[index] = '\0';
            strncpy(out, buffer, max_len);
            out[max_len - 1] = '\0';

            index = 0;
            return true;
        }

        if (index < UART_TOKEN_MAX_LEN - 1) {
            buffer[index++] = c;
        } else {
            index = 0;
        }
    }

    return false;
}


int32_t move_geneva_slots(motor_driver_t *m, encoder_t *enc, int32_t requested_slots)
{
    if (requested_slots <= 0) {
        return 0;
    }

    int32_t start_counts = encoder_get_position(enc);
    uint32_t start_edges = encoder_get_quad_edge_count(enc);
    int32_t start_slot = encoder_get_slot(enc, COUNTS_PER_SLOT, SLOT_THRESHOLD_COUNTS);
    int32_t target_slot = start_slot + requested_slots;

    printf("move_geneva_slots() START\n");
    printf("  start_counts    = %ld\n", (long)start_counts);
    printf("  start_quad_edges= %lu\n", (unsigned long)start_edges);
    printf("  start_slot      = %ld\n", (long)start_slot);
    printf("  requested_slots = %ld\n", (long)requested_slots);
    printf("  target_slot     = %ld\n", (long)target_slot);

    motor_forward_full(m);

    int timeout = 0;

    while (1) {
        int32_t current_counts = encoder_get_position(enc);
        int32_t current_slot = encoder_get_slot(enc, COUNTS_PER_SLOT, SLOT_THRESHOLD_COUNTS);

        if (timeout % 500 == 0) {
            printf("  loop: current_counts=%ld current_slot=%ld target_slot=%ld\n",
                   (long)current_counts,
                   (long)current_slot,
                   (long)target_slot);
        }

        if (current_slot >= target_slot) {
            printf("  target reached\n");
            break;
        }

        sleep_us(100);
        timeout++;

        if (timeout > MOVE_TIMEOUT_MS) {
            printf("  TIMEOUT in encoder loop\n");
            break;
        }
    }

    motor_stop(m);
    sleep_ms(10);

    int32_t end_counts = encoder_get_position(enc);
    uint32_t end_edges = encoder_get_quad_edge_count(enc);
    int32_t end_slot = encoder_get_slot(enc, COUNTS_PER_SLOT, SLOT_THRESHOLD_COUNTS);
    int32_t actual_slots_moved = end_slot - start_slot;

    printf("move_geneva_slots() END\n");
    printf("  end_counts         = %ld\n", (long)end_counts);
    printf("  end_quad_edges     = %lu\n", (unsigned long)end_edges);
    printf("  end_slot           = %ld\n", (long)end_slot);
    printf("  actual_slots_moved = %ld\n", (long)actual_slots_moved);

    return actual_slots_moved;
}


int32_t move_one_geneva_slot(motor_driver_t *m, encoder_t *enc)
{
    return move_geneva_slots(m, enc, 1);
}


// ---------------- motors ----------------
motor_driver_t m1 = { .pwm_pin = 0, .wrap = 10000, .clkdiv = 4.0f };
motor_driver_t m2 = { .pwm_pin = 1, .wrap = 10000, .clkdiv = 4.0f };
motor_driver_t m3 = { .pwm_pin = 2, .wrap = 10000, .clkdiv = 4.0f };
motor_driver_t m4 = { .pwm_pin = 3, .wrap = 10000, .clkdiv = 4.0f };
motor_driver_t m5 = { .pwm_pin = 4, .wrap = 10000, .clkdiv = 4.0f };
motor_driver_t m6 = { .pwm_pin = 5, .wrap = 10000, .clkdiv = 4.0f };
motor_driver_t m7 = { .pwm_pin = 6, .wrap = 10000, .clkdiv = 4.0f };
motor_driver_t m8 = { .pwm_pin = 7, .wrap = 10000, .clkdiv = 4.0f };


// ---------------- encoders ----------------
encoder_t enc1 = { .pin_a = 8,  .pin_b = 9,  .use_pullups = true };
encoder_t enc2 = { .pin_a = 10, .pin_b = 11, .use_pullups = true };
encoder_t enc3 = { .pin_a = 12, .pin_b = 13, .use_pullups = true };
encoder_t enc4 = { .pin_a = 14, .pin_b = 15, .use_pullups = true };
encoder_t enc5 = { .pin_a = 18, .pin_b = 19, .use_pullups = true };
encoder_t enc6 = { .pin_a = 20, .pin_b = 21, .use_pullups = true };
encoder_t enc7 = { .pin_a = 22, .pin_b = 26, .use_pullups = true };
encoder_t enc8 = { .pin_a = 27, .pin_b = 28, .use_pullups = true };


// ---------------- arrays ----------------
motor_driver_t* motors[8] = {
    &m1, &m2, &m3, &m4, &m5, &m6, &m7, &m8
};

encoder_t* encoders[8] = {
    &enc1, &enc2, &enc3, &enc4, &enc5, &enc6, &enc7, &enc8
};


int main()
{
    stdio_init_all();

    printf("Starting UART motor control program\n");

    motor_init(&m1);
    motor_init(&m2);
    motor_init(&m3);
    motor_init(&m4);
    motor_init(&m5);
    motor_init(&m6);
    motor_init(&m7);
    motor_init(&m8);

    encoder_init(&enc1);
    encoder_init(&enc2);
    encoder_init(&enc3);
    encoder_init(&enc4);
    encoder_init(&enc5);
    encoder_init(&enc6);
    encoder_init(&enc7);
    encoder_init(&enc8);

    uart_comm_init();

    uart_state_t state = WAIT_FIRST_TOKEN;

    char token[UART_TOKEN_MAX_LEN];

    int32_t requested_motor = 0;
    int32_t requested_slots = 0;

    while (1) {

        if (uart_read_token(token, UART_TOKEN_MAX_LEN)) {

            printf("UART token received: %s\n", token);

            if (state == WAIT_FIRST_TOKEN) {

                if (strcmp(token, "a") == 0 || strcmp(token, "A") == 0) {
                    printf("Command A received. Next token should be motor number.\n");
                    state = WAIT_A_MOTOR;
                } else {
                    requested_motor = atoi(token);
                    printf("Motor number received first: %ld\n", (long)requested_motor);
                    state = WAIT_SLOT_COUNT;
                }
            }

            else if (state == WAIT_A_MOTOR) {

                requested_motor = atoi(token);

                if (requested_motor >= 1 && requested_motor <= 8) {

                    int index = requested_motor - 1;

                    printf("Moving motor %ld by ONE slot\n", (long)requested_motor);

                    int32_t actual_slots_moved = move_one_geneva_slot(
                        motors[index],
                        encoders[index]
                    );

                    printf("ABOUT TO SEND UART RESPONSE: %ld\n",
                        (long)actual_slots_moved);

                        uart_comm_send_int(actual_slots_moved);

                    printf("UART RESPONSE SENT\n");

                } else {
                    printf("Invalid motor number: %ld\n", (long)requested_motor);
                    uart_comm_send_int(-1);
                }

                requested_motor = 0;
                requested_slots = 0;
                state = WAIT_FIRST_TOKEN;
            }

            else if (state == WAIT_SLOT_COUNT) {

                requested_slots = atoi(token);

                if (requested_motor >= 1 && requested_motor <= 8) {

                    int index = requested_motor - 1;

                    printf("Moving motor %ld by %ld slots\n",
                           (long)requested_motor,
                           (long)requested_slots);

                    int32_t actual_slots_moved = move_geneva_slots(
                        motors[index],
                        encoders[index],
                        requested_slots
                    );

                    printf("ABOUT TO SEND UART RESPONSE: %ld\n",
                  (long)actual_slots_moved);

                uart_comm_send_int(actual_slots_moved);

                printf("UART RESPONSE SENT\n");

                } else {
                    printf("Invalid motor number: %ld\n", (long)requested_motor);
                    uart_comm_send_int(-1);
                }

                requested_motor = 0;
                requested_slots = 0;
                state = WAIT_FIRST_TOKEN;
            }
        }

        sleep_ms(5);
    }
}
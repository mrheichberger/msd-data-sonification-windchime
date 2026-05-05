#include "motor_driver.h"
#include "encoder.h"
#include <pico/stdlib.h>
#include <pico/time.h>
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
#define SLOT_THRESHOLD_COUNTS 2
#define MOVE_TIMEOUT_MS 60000
#define NO_MOTION_TIMEOUT_MS 2500
#define SETTLE_TIME_MS 120
#define SETTLE_TIMEOUT_MS 1000
#define SLOWDOWN_SLOTS 1

#define UART_TOKEN_MAX_LEN 16
#define CMD_QUEUE_SIZE 16


typedef enum {
    WAIT_FIRST_TOKEN,
    WAIT_A_MOTOR,
    WAIT_SLOT_COUNT
} uart_state_t;


typedef struct {
    int32_t motor_num;
    int32_t slots;
} motor_cmd_t;


static motor_cmd_t cmd_queue[CMD_QUEUE_SIZE];
static int q_head = 0;
static int q_tail = 0;
static int q_count = 0;


bool queue_push(int32_t motor_num, int32_t slots)
{
    if (q_count >= CMD_QUEUE_SIZE) {
        return false;
    }

    cmd_queue[q_tail].motor_num = motor_num;
    cmd_queue[q_tail].slots = slots;

    q_tail = (q_tail + 1) % CMD_QUEUE_SIZE;
    q_count++;

    return true;
}


bool queue_pop(motor_cmd_t *cmd)
{
    if (q_count <= 0) {
        return false;
    }

    *cmd = cmd_queue[q_head];

    q_head = (q_head + 1) % CMD_QUEUE_SIZE;
    q_count--;

    return true;
}


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

    printf("move_geneva_slots() START\n");
    printf("  start_counts    = %ld\n", (long)start_counts);
    printf("  start_quad_edges= %lu\n", (unsigned long)start_edges);
    printf("  start_slot      = %ld\n", (long)start_slot);
    printf("  requested_slots = %ld\n", (long)requested_slots);
    printf("  target_delta    = %ld\n", (long)requested_slots);

    motor_forward_full(m);

    uint32_t start_time = to_ms_since_boot(get_absolute_time());
    uint32_t last_motion_time = start_time;
    int32_t prev_counts = start_counts;
    uint32_t print_counter = 0;

    while (1) {
        uint32_t now_ms = to_ms_since_boot(get_absolute_time());
        int32_t current_counts = encoder_get_position(enc);
        int32_t current_slot = encoder_get_slot(enc, COUNTS_PER_SLOT, SLOT_THRESHOLD_COUNTS);
        int32_t moved_slots = current_slot - start_slot;
        int32_t remaining_slots = requested_slots - moved_slots;

        if (current_counts != prev_counts) {
            last_motion_time = now_ms;
            prev_counts = current_counts;
        }

        if (remaining_slots <= SLOWDOWN_SLOTS) {
            // Slow down near target to reduce overshoot/coast.
            motor_set_speed(m, 0.40f);
        }

        if (print_counter % 500 == 0) {
    printf("  loop: current_counts=%ld current_slot=%ld moved=%ld remaining=%ld\n",
           (long)current_counts,
           (long)current_slot,
           (long)moved_slots,
           (long)remaining_slots);
}

        if (moved_slots >= requested_slots) {
            printf("  target reached\n");
            break;
        }

        if (now_ms - start_time > MOVE_TIMEOUT_MS) {
            printf("  TIMEOUT in encoder loop\n");
            break;
        }

        if (now_ms - last_motion_time > NO_MOTION_TIMEOUT_MS) {
            printf("  NO_MOTION timeout in encoder loop\n");
            break;
        }

        print_counter++;
        sleep_us(100);
    }

    motor_stop(m);

    // Wait for encoder to settle after stop before reporting slots moved.
    uint32_t settle_start = to_ms_since_boot(get_absolute_time());
    uint32_t stable_since = settle_start;
    int32_t settle_prev_counts = encoder_get_position(enc);
    while (1) {
        sleep_ms(5);
        uint32_t now_ms = to_ms_since_boot(get_absolute_time());
        int32_t counts_now = encoder_get_position(enc);

        if (counts_now != settle_prev_counts) {
            stable_since = now_ms;
            settle_prev_counts = counts_now;
        }

        if (now_ms - stable_since >= SETTLE_TIME_MS) {
            break;
        }

        if (now_ms - settle_start >= SETTLE_TIMEOUT_MS) {
            printf("  settle timeout\n");
            break;
        }
    }

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

    bool motor_busy = false;

    while (1) {

        // ----------------------------------------------------
        // 1. Only read UART when motor is NOT busy
        // ----------------------------------------------------
        if (!motor_busy && uart_read_token(token, UART_TOKEN_MAX_LEN)) {

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

                if (queue_push(requested_motor, 1)) {
                    printf("Queued one-slot command: motor=%ld slots=1\n",
                           (long)requested_motor);
                } else {
                    printf("Command queue full\n");
                    uart_comm_send_int(-88);
                }

                requested_motor = 0;
                requested_slots = 0;
                state = WAIT_FIRST_TOKEN;
            }

            else if (state == WAIT_SLOT_COUNT) {

                requested_slots = atoi(token);

                if (queue_push(requested_motor, requested_slots)) {
                    printf("Queued normal command: motor=%ld slots=%ld\n",
                           (long)requested_motor,
                           (long)requested_slots);
                } else {
                    printf("Command queue full\n");
                    uart_comm_send_int(-88);
                }

                requested_motor = 0;
                requested_slots = 0;
                state = WAIT_FIRST_TOKEN;
            }
        }


        // ----------------------------------------------------
        // 2. Process exactly ONE queued command at a time
        // ----------------------------------------------------
        if (!motor_busy) {

            motor_cmd_t cmd;

            if (queue_pop(&cmd)) {

                motor_busy = true;

                printf("Processing command: motor=%ld slots=%ld\n",
                       (long)cmd.motor_num,
                       (long)cmd.slots);

                int32_t actual_slots_moved = -1;

                if (cmd.motor_num >= 1 && cmd.motor_num <= 8 && cmd.slots > 0) {

                    int index = cmd.motor_num - 1;

                    actual_slots_moved = move_geneva_slots(
                        motors[index],
                        encoders[index],
                        cmd.slots
                    );

                } else {
                    printf("Invalid command: motor=%ld slots=%ld\n",
                           (long)cmd.motor_num,
                           (long)cmd.slots);

                    actual_slots_moved = -1;
                }

                printf("ABOUT TO SEND UART RESPONSE: %ld\n",
                       (long)actual_slots_moved);

                uart_comm_send_int(actual_slots_moved);

                printf("UART RESPONSE SENT\n");

                motor_busy = false;
            }
        }

        sleep_ms(2);
    }
} 
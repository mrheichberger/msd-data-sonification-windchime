#include "motor_driver.h"
#include "encoder.h"
#include <pico/stdlib.h>
#include <stdio.h>
#include <stdbool.h>
#include "uart_comm.h"


#define COUNTS_PER_SLOT 16
#define MOVE_TIMEOUT_MS 15000

int32_t move_geneva_slots(motor_driver_t *m, encoder_t *enc, int32_t requested_slots)
{
    if (requested_slots <= 0) {
        return 0;
    }
    
    int32_t start_counts = encoder_get_position(enc);
    int32_t target_counts = start_counts + (requested_slots * COUNTS_PER_SLOT);

    printf("move_geneva_slots() START\n");
    printf("  start_counts    = %ld\n", (long)start_counts);
    printf("  requested_slots = %ld\n", (long)requested_slots);
    printf("  target_counts   = %ld\n", (long)target_counts);

    motor_forward_full(m);

    int timeout = 0;

    while (1) {
        int32_t current_counts = encoder_get_position(enc);

        if (timeout % 500 == 0) {
            printf("  loop: current_counts=%ld target_counts=%ld\n",
                   (long)current_counts, (long)target_counts);
        }

        if (current_counts >= target_counts) {
            printf("  target reached\n");
            break;
        }

        sleep_ms(1);
        timeout++;

        if (timeout > MOVE_TIMEOUT_MS) {
            printf("  TIMEOUT in encoder loop\n");
            break;
        }
    }

    motor_stop(m);
    sleep_ms(10);

    int32_t end_counts = encoder_get_position(enc);
    int32_t actual_slots_moved = (end_counts - start_counts) / COUNTS_PER_SLOT;

    printf("move_geneva_slots() END\n");
    printf("  end_counts         = %ld\n", (long)end_counts);
    printf("  actual_slots_moved = %ld\n", (long)actual_slots_moved);

    return actual_slots_moved;
}

/*
   int32_t move_geneva_slots(motor_driver_t *m, encoder_t *enc, int32_t requested_slots)
{
    if (requested_slots <= 0) {
        return 0;
    }

    int32_t start_slot = encoder_get_slot(enc, COUNTS_PER_SLOT, SLOT_THRESHOLD);
    int32_t target_slot = start_slot + requested_slots;

    printf("move_geneva_slots() START\n");
    printf("  start_slot      = %ld\n", (long)start_slot);
    printf("  requested_slots = %ld\n", (long)requested_slots);
    printf("  target_slot     = %ld\n", (long)target_slot);

    motor_forward_full(m);

    int timeout = 0;

    while (1) {
        int32_t current_slot = encoder_get_slot(enc, COUNTS_PER_SLOT, SLOT_THRESHOLD);

        if (timeout % 500 == 0) {
            int32_t pos = encoder_get_position(enc);
            printf("  loop: pos=%ld current_slot=%ld target_slot=%ld\n",
                   (long)pos, (long)current_slot, (long)target_slot);
        }

        if (current_slot >= target_slot) {
            printf("  target reached\n");
            break;
        }

        sleep_ms(1);
        timeout++;

        if (timeout > MOVE_TIMEOUT_MS) {
            printf("  TIMEOUT in encoder loop\n");
            break;
        }
    }

    motor_stop(m);
    sleep_ms(10);

    int32_t end_slot = encoder_get_slot(enc, COUNTS_PER_SLOT, SLOT_THRESHOLD);
    int32_t actual_slots_moved = end_slot - start_slot;

    printf("move_geneva_slots() END\n");
    printf("  end_slot           = %ld\n", (long)end_slot);
    printf("  actual_slots_moved = %ld\n", (long)actual_slots_moved);

    return actual_slots_moved;
}
*/

// ---------------- motors ----------------
motor_driver_t m1 = {
    .pwm_pin = 0,
    .wrap = 10000,
    .clkdiv = 4.0f
};

motor_driver_t m2 = {
    .pwm_pin = 1,
    .wrap = 10000,
    .clkdiv = 4.0f
};

motor_driver_t m3 = {
    .pwm_pin = 2,
    .wrap = 10000,
    .clkdiv = 4.0f
};

motor_driver_t m4 = {
    .pwm_pin = 3,
    .wrap = 10000,
    .clkdiv = 4.0f
};

motor_driver_t m5 = {
    .pwm_pin = 4,
    .wrap = 10000,
    .clkdiv = 4.0f
};

motor_driver_t m6 = {
    .pwm_pin = 5,
    .wrap = 10000,
    .clkdiv = 4.0f
};

motor_driver_t m7 = {
    .pwm_pin = 6,
    .wrap = 10000,
    .clkdiv = 4.0f
};

motor_driver_t m8 = {
    .pwm_pin = 7,
    .wrap = 10000,
    .clkdiv = 4.0f
};

// ---------------- encoders ----------------
encoder_t enc1 = {
    .pin_a = 8,
    .pin_b = 9,
    .use_pullups = true
};

encoder_t enc2 = {
    .pin_a = 10,
    .pin_b = 11,
    .use_pullups = true
};

encoder_t enc3 = {
    .pin_a = 12,
    .pin_b = 13,
    .use_pullups = true
};

encoder_t enc4 = {
    .pin_a = 14,
    .pin_b = 15,
    .use_pullups = true
};

encoder_t enc5 = {
    .pin_a = 18,
    .pin_b = 19,
    .use_pullups = true
};

encoder_t enc6 = {
    .pin_a = 20,
    .pin_b = 21,
    .use_pullups = true
};

encoder_t enc7 = {
    .pin_a = 22,
    .pin_b = 26,
    .use_pullups = true
};

encoder_t enc8 = {
    .pin_a = 27,
    .pin_b = 28,
    .use_pullups = true
};

// ---------------- arrays ----------------
motor_driver_t* motors[8] = { &m1, &m2, &m3, &m4, &m5, &m6, &m7, &m8 };
encoder_t* encoders[8] = { &enc1, &enc2, &enc3, &enc4, &enc5, &enc6, &enc7, &enc8 };
/*
int main() {
    stdio_init_all();

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

    sleep_ms(2000);  // gives COM port time to connect

    printf("Motor 3 encoder calibration test\n");
    printf("Resetting encoder 3 to zero...\n");

    encoder_reset(&enc3);

    printf("Starting motor 3 now\n");
    motor_forward_full(&m3);

    while (1) {
        int32_t pos = encoder_get_position(&enc3);
        printf("Encoder count: %ld\n", (long)pos);
        sleep_ms(200);
    }
}
    */

int main() {
    stdio_init_all();

    printf("Starting motor control + UART debug program\n");

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

    int32_t requested_motor = 0;
    int32_t requested_slots = 0;
    bool motor_received = false;

    while (1) {
        //--------------

        //just for debug start here 

        /*
  printf("TURNING ALL MOTORS ON\n");

    // Turn all motors ON
    for (int i = 0; i < 8; i++) {
        motor_forward_full(motors[i]);
    }

    sleep_ms(10000); // 10 seconds ON

    printf("TURNING ALL MOTORS OFF\n");

    // Turn all motors OFF
    for (int i = 0; i < 8; i++) {
        motor_stop(motors[i]);
    }

    sleep_ms(5000); // 5 seconds OFF
}}

//-------------------
        //just for debug end here

        */
        
        if (!motor_received) {
            if (uart_comm_read_int(&requested_motor)) {
                printf("UART received motor number: %ld\n", (long)requested_motor);
                motor_received = true;
            }
        } else {
            if (uart_comm_read_int(&requested_slots)) {
                printf("UART received slots: %ld\n", (long)requested_slots);

                if (requested_motor >= 1 && requested_motor <= 8) {
                    int index = requested_motor - 1;

                    printf("About to move motor %ld (index %d) by %ld slots\n",
                           (long)requested_motor, index, (long)requested_slots);

                    int32_t actual_slots_moved = move_geneva_slots(
                        motors[index],
                        encoders[index],
                        requested_slots
                    );

                    printf("Sending actual_slots_moved back over UART: %ld\n",
                           (long)actual_slots_moved);
                    uart_comm_send_int(actual_slots_moved);
                } else {
                    printf("Invalid motor number: %ld\n", (long)requested_motor);
                    uart_comm_send_int(-1);
                }

                motor_received = false;
            }
        }

        sleep_ms(5);
    }
}


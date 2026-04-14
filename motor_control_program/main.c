//Motor Control Prototype Program
//Intended for testing basic GPIO functionality on the Raspberry Pi Pico.


#include "motor_driver.h"
#include "encoder.h"
#include <pico/stdlib.h>
#include <stdio.h>
#include <stdbool.h>
#include "uart_comm.h"
#define COUNTS_PER_DETENT 4
#define UART_TX_PIN 16
#define UART_RX_PIN 17

//-------------------------function to move motors the correct amount of sport ----
//---------------------------main control logic ---------------------------
motor_driver_t* motors[8] = { &m1, &m2, &m3, &m4, &m5, &m6, &m7, &m8 };
encoder_t* encoders[8] = { &enc1, &enc2, &enc3, &enc4, &enc5, &enc6, &enc7, &enc8 };

int32_t move_geneva_slots(motor_driver_t *m, encoder_t *enc, int32_t requested_slots)
{
    int32_t start_pos = encoder_get_position(enc);
    int32_t start_det = start_pos / COUNTS_PER_DETENT;
    int32_t start_slot = start_det / DETENTS_PER_SLOT;

    int32_t target_slot = start_slot + requested_slots;

    motor_forward_full(m);

    while (1) {
        int32_t pos = encoder_get_position(enc);
        int32_t det = pos / COUNTS_PER_DETENT;
        int32_t current_slot = det / DETENTS_PER_SLOT;

        if (current_slot >= target_slot) {
            break;
        }

        sleep_ms(1);
    }

    motor_stop(m);
    sleep_ms(10);

    int32_t end_pos = encoder_get_position(enc);
    int32_t end_det = end_pos / COUNTS_PER_DETENT;
    int32_t end_slot = end_det / DETENTS_PER_SLOT;

    return end_slot - start_slot;
}
//------------------------------------------------------------------------

motor_driver_t m1 = { //maps to 1
    .pwm_pin = 0,
    .wrap = 10000,
    .clkdiv = 4.0f
};

motor_driver_t m2 = { //maos to 2
    .pwm_pin = 1,
    .wrap = 10000,
    .clkdiv = 4.0f
};

motor_driver_t m3 = { //maps to 4
    .pwm_pin = 2,
    .wrap = 10000,
    .clkdiv = 4.0f
};

motor_driver_t m4 = { //maps to 5
    .pwm_pin = 3,
    .wrap = 10000,
    .clkdiv = 4.0f
};
motor_driver_t m5 = { //maps to 6
    .pwm_pin = 4,
    .wrap = 10000,
    .clkdiv = 4.0f
};

motor_driver_t m6 = { //maps to 7
    .pwm_pin = 5,
    .wrap = 10000,
    .clkdiv = 4.0f
};

motor_driver_t m7 = { //maps to 9
    .pwm_pin = 6,
    .wrap = 10000,
    .clkdiv = 4.0f
};

motor_driver_t m8 = { //maps to number 10 
    .pwm_pin = 7,
    .wrap = 10000,
    .clkdiv = 4.0f
};

//class values for encoder mapped to 
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
//UART is 16/17
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
 
//--------------------------------------------------------------

int main() {
//----------one time initalizations ----------------------------
    stdio_init_all();
    motor_init(&m1); //initalize motor 1
    motor_init(&m2); //initalize motor 2
    motor_init(&m3); //initalize motor 1
    motor_init(&m4); //initalize motor 2
    motor_init(&m5); //initalize motor 1
    motor_init(&m6); //initalize motor 2
    motor_init(&m7); //initalize motor 1
    motor_init(&m8); //initalize motor 2
    encoder_init(&enc1); //initalize the encoder
    encoder_init(&enc2);
    encoder_init(&enc3);
    encoder_init(&enc4);
    encoder_init(&enc5);
    encoder_init(&enc6);
    encoder_init(&enc7);
    encoder_init(&enc8);
    uart_comm_init();

//initalize variables to say hold what uart info is transferring 
int32_t requested_motor = 0;
int32_t requested_slots = 0;
int32_t actual_slots_moved = 0;

  
while (1) {
    int32_t requested_motor = 0;
    int32_t requested_slots = 0;
    int32_t actual_slots_moved = 0;

    if (uart_comm_read_int(&requested_motor)) {
        if (uart_comm_read_int(&requested_slots)) {

            if (requested_motor >= 1 && requested_motor <= 8) {
                int index = requested_motor - 1;

                actual_slots_moved = move_geneva_slots(
                    motors[index],
                    encoders[index],
                    requested_slots
                );

                uart_comm_send_int(actual_slots_moved);
            } else {
                uart_comm_send_int(-1);
            }
        }
    }

    sleep_ms(5);
}

}











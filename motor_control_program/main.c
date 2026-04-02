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
//------------------------------------------------------------------------
//class values for motor #1 mapped to pin 0 and 1
motor_driver_t m1 = {
    .in1_pin = 0,
    .in2_pin = 1,
    .wrap = 10000,
    .clkdiv = 4.0f
};

//class values for motor # 2 mapped to pin 2 and 3
motor_driver_t m2 = {
    .in1_pin = 2,
    .in2_pin = 3,
    .wrap = 10000,
    .clkdiv = 4.0f
};

//class values for encoder mapped to pins 6 and 7
    encoder_t enc = {
        .pin_a = 6,
        .pin_b = 7,
        .use_pullups = true
    };
 
//--------------------------------------------------------------

int main() {
//----------one time initalizations ----------------------------
    stdio_init_all();
    motor_init(&m1); //initalize motor 1
    motor_init(&m2); //initalize motor 2
    encoder_init(&enc); //initalize the encoder
    uart_comm_init();

    //reading this number in 
    int32_t requested_slots = 0;
    //writing back to this variable 
    int32_t actual_slots_moved = 0;


while(1) {  //keep this loop going forever 
  
    //----------------encoder protocal ------------------------------------
    //get the encoder position and send to putty 
    int32_t pos = encoder_get_position();
    int32_t det = pos / 4;
    int32_t rot = encoder_get_slot(16, 2);
    printf("pos=%ld det=%ld rot60=%ld\n", pos, det, rot);

    //------------------motor protocal ------------------------------------    
    //turn the motors on with pmw=1
    motor_forward_full(&m2); //make output A of motor logic high
    motor_forward_full(&m1); //make output B of motor logic low
    sleep_ms(100);

    //------------uart protocal -------------------------------------------
     if (uart_comm_read_int(&requested_slots)) {
            // Replace this with your real motion logic
            //actual_slots_moved = move_geneva_slots(requested_slots);

            actual_slots_moved = rot;  // temporary test infinite count up just to see how it writes back
            uart_comm_send_int(actual_slots_moved);
             // Send encoder position back over UART pins
        }

        sleep_ms(5);
    //-----------------------------------------------------------------------

}
}


/* create the move_geneva_slots function that: 
reads current encoder position
computes target
drives motor
stops when target reached
returns actual number of slots moved*/








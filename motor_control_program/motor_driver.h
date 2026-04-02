#ifndef MOTOR_DRIVER_H
#define MOTOR_DRIVER_H

#include <stdbool.h>
#include <stdint.h>

typedef struct {
    uint8_t in1_pin;
    uint8_t in2_pin;
   // uint8_t sleep_pin;

    uint16_t wrap;
    float clkdiv;
} motor_driver_t;

void motor_init(motor_driver_t *m);

/**
 * speed in range [-1.0, +1.0]
 * sign = direction
 * magnitude = duty cycle
 */
void motor_set_speed(motor_driver_t *m, float speed);

void motor_forward_full(motor_driver_t *m); 
//for motor fully on one direction at full speed 

void motor_stop(motor_driver_t *m); //to stop the motor from moving 
//

#endif

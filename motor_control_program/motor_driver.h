#ifndef MOTOR_DRIVER_H
#define MOTOR_DRIVER_H

#include <stdint.h>

typedef struct {
    uint8_t pwm_pin;
    uint16_t wrap;
    float clkdiv;
} motor_driver_t;

void motor_init(motor_driver_t *m);
void motor_set_speed(motor_driver_t *m, float speed);
void motor_forward_full(motor_driver_t *m);
void motor_stop(motor_driver_t *m);

#endif
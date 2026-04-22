//--------------------------------------------------------------
//motor_driver.c
//program containing functions to move motors for either 
//rotating sets
//
//---------------------------------------------------------------

//libraries 
#include "motor_driver.h"
#include "pico/stdlib.h"
#include "hardware/pwm.h"
#include <math.h>



//function to set PWM slice 
static uint pwm_slice_for_gpio(uint gpio) {
    gpio_set_function(gpio, GPIO_FUNC_PWM);
    return pwm_gpio_to_slice_num(gpio);
}


//function to initalize the motors 
void motor_init(motor_driver_t *m)
{
    uint slice = pwm_slice_for_gpio(m->pwm_pin);

    pwm_config cfg = pwm_get_default_config();
    pwm_config_set_wrap(&cfg, m->wrap ? m->wrap : 10000);
    pwm_config_set_clkdiv(&cfg, m->clkdiv ? m->clkdiv : 4.0f);

    pwm_init(slice, &cfg, true);
    pwm_set_gpio_level(m->pwm_pin, 0);
}


//function to set motor speed 
//currently not being used, rough prototype only 
/*void motor_set_speed(motor_driver_t *m, float speed)
{
    if (speed > 1.0f) speed = 1.0f;
    if (speed < -1.0f) speed = -1.0f;

    float mag = fabsf(speed);
    uint16_t wrap = m->wrap ? m->wrap : 10000;
    uint16_t level = (uint16_t)(mag * wrap);

    if (speed > 0) {
        // IN1 = PWM, IN2 = 0
        pwm_set_gpio_level(m->in1_pin, level);
        pwm_set_gpio_level(m->in2_pin, 0);
    } else if (speed < 0) {
        // IN2 = PWM, IN1 = 0
        pwm_set_gpio_level(m->in1_pin, 0);
        pwm_set_gpio_level(m->in2_pin, level);
    } else {
        // Coast
        pwm_set_gpio_level(m->in1_pin, 0);
        pwm_set_gpio_level(m->in2_pin, 0);
    }
}
*/
void motor_set_speed(motor_driver_t *m, float speed)
{
    if (speed > 1.0f) speed = 1.0f;
    if (speed < 0.0f) speed = 0.0f;

    uint16_t wrap = m->wrap ? m->wrap : 10000;
    uint16_t level = (uint16_t)(speed * wrap);

    pwm_set_gpio_level(m->pwm_pin, level);
}

//function to turn motor on full forward speed 
//turns 1 input to 12 v and other pin to 0v
    void motor_forward_full(motor_driver_t *m)
{
    uint16_t wrap = m->wrap ? m->wrap : 10000;
    pwm_set_gpio_level(m->pwm_pin, 0.85f * wrap);
    //pwm_set_gpio_level(m->pwm_pin, wrap);
}


//motor function to stop motors from moving, turn both pins to 0V
void motor_stop(motor_driver_t *m)
{
    pwm_set_gpio_level(m->pwm_pin, 0);
}

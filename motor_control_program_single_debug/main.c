#include "../motor_control_program/motor_driver.h"
#include "../motor_control_program/encoder.h"
#include <pico/stdlib.h>
#include <stdio.h>

#define SAMPLE_MS 20

int main(void)
{
    stdio_init_all();
    sleep_ms(2000);

    motor_driver_t motor = {
        .pwm_pin = 0,
        .wrap = 10000,
        .clkdiv = 4.0f,
    };

    encoder_t encoder = {
        .pin_a = 8,
        .pin_b = 9,
        .use_pullups = true,
    };

    motor_init(&motor);
    encoder_init(&encoder);

    printf("\n=== RAW ENCODER DEBUG ===\n");
    printf("Rotate ONE Geneva slot manually or let motor run slowly.\n");
    printf("We will measure position change between slot clicks.\n\n");

    // Optional: run motor (LOW SPEED preferred if you can)
    motor_forward_full(&motor);

    int32_t last_pos = encoder_get_position(&encoder);

    while (1)
    {
        sleep_ms(SAMPLE_MS);

        int32_t pos = encoder_get_position(&encoder);
        int32_t delta = pos - last_pos;

        // Only print when meaningful movement happens
        if (delta != 0)
        {
            printf("pos=%ld  delta=%ld\n", (long)pos, (long)delta);
            last_pos = pos;
        }
    }
}
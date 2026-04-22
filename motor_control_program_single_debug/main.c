#include "../motor_control_program/motor_driver.h"
#include "../motor_control_program/encoder.h"
#include <hardware/gpio.h>
#include <pico/stdlib.h>
#include <pico/time.h>
#include <stdio.h>

#define TEST_MOTOR_NUM 1
#define GENEVA_SLOTS_PER_REV 6
#ifndef QUADRATURE_COUNTS_PER_GENEVA_SLOT
#define QUADRATURE_COUNTS_PER_GENEVA_SLOT 16
#endif
#define COUNTS_PER_SLOT QUADRATURE_COUNTS_PER_GENEVA_SLOT
#define SLOT_THRESHOLD_COUNTS 3

/* USB serial (PuTTY) sample period ms */
#define SAMPLE_MS 15
/* Also print a compact line every N ms even if slot unchanged */
#define TICK_MS 100

static inline uint8_t ab_state(const encoder_t *e) {
    uint8_t a = gpio_get(e->pin_a) ? 1U : 0U;
    uint8_t b = gpio_get(e->pin_b) ? 1U : 0U;
    return (uint8_t)((a << 1) | b);
}

int main(void) {
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

    printf("\r\n");
    printf("=== FULL FORWARD + USB serial log (PuTTY) ===\r\n");
    printf("motor=%d pwm_pin=%d enc A=GPIO%d B=GPIO%d\r\n",
           TEST_MOTOR_NUM, motor.pwm_pin, encoder.pin_a, encoder.pin_b);
    printf("geneva_slots=%d quad_counts/slot=%d threshold=%d\r\n",
           GENEVA_SLOTS_PER_REV, COUNTS_PER_SLOT, SLOT_THRESHOLD_COUNTS);
    printf("Motor runs FORWARD continuously. Log on each SLOT change + tick.\r\n");
    printf("ab=2-bit Gray state (0..3). pos=quad-integrated. edges=valid QDEC steps.\r\n\r\n");

    motor_forward_full(&motor);

    int32_t last_slot = encoder_get_slot(&encoder, COUNTS_PER_SLOT, SLOT_THRESHOLD_COUNTS);
    int32_t last_pos = encoder_get_position(&encoder);
    uint32_t last_edges = encoder_get_quad_edge_count(&encoder);
    uint8_t last_ab = ab_state(&encoder);

    absolute_time_t last_tick = get_absolute_time();

    for (;;) {
        sleep_ms(SAMPLE_MS);

        int32_t pos = encoder_get_position(&encoder);
        uint32_t edges = encoder_get_quad_edge_count(&encoder);
        int32_t slot = encoder_get_slot(&encoder, COUNTS_PER_SLOT, SLOT_THRESHOLD_COUNTS);
        uint8_t ab = ab_state(&encoder);

        uint32_t t_ms = to_ms_since_boot(get_absolute_time());

        if (ab != last_ab) {
            printf("[AB] t=%lums ab %u -> %u  pos=%ld edges=%lu slot=%ld\r\n",
                   (unsigned long)t_ms, (unsigned)last_ab, (unsigned)ab,
                   (long)pos, (unsigned long)edges, (long)slot);
            last_ab = ab;
        }

        if (slot != last_slot) {
            int32_t d_pos = pos - last_pos;
            uint32_t d_edges = edges - last_edges;
            printf("\r\n");
            printf("*** SLOT_BOUNDARY t=%lums slot %ld -> %ld | pos=%ld d_pos=%ld | edges=%lu d_edges=%lu ***\r\n",
                   (unsigned long)t_ms, (long)last_slot, (long)slot,
                   (long)pos, (long)d_pos,
                   (unsigned long)edges, (unsigned long)d_edges);
            printf("\r\n");
            last_slot = slot;
            last_pos = pos;
            last_edges = edges;
        }

        if (absolute_time_diff_us(last_tick, get_absolute_time()) >= (int64_t)TICK_MS * 1000) {
            last_tick = get_absolute_time();
            printf("[tick] t=%lums ab=%u pos=%ld edges=%lu slot=%ld\r\n",
                   (unsigned long)t_ms, (unsigned)ab,
                   (long)pos, (unsigned long)edges, (long)slot);
        }
    }
}

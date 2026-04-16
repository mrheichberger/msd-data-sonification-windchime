#include "encoder.h"
#include "pico/stdlib.h"
#include "hardware/sync.h"

#define MAX_GPIO 30

// Map each GPIO number to the encoder that owns it
static encoder_t *gpio_to_encoder[MAX_GPIO] = {0};
static bool encoder_irq_callback_installed = false;

// Quadrature lookup table
static const int8_t QDEC_TABLE[16] = {
     0, -1, +1,  0,
    +1,  0,  0, -1,
    -1,  0,  0, +1,
     0, +1, -1,  0
};

static inline uint8_t encoder_read_state(const encoder_t *e) {
    uint8_t a = gpio_get(e->pin_a) ? 1 : 0;
    uint8_t b = gpio_get(e->pin_b) ? 1 : 0;
    return (uint8_t)((a << 1) | b);
}

static void encoder_gpio_isr(uint gpio, uint32_t events) {
    (void)events;

    if (gpio >= MAX_GPIO) {
        return;
    }

    encoder_t *e = gpio_to_encoder[gpio];
    if (e == NULL) {
        return;
    }

    uint8_t new_state = encoder_read_state(e);
    uint8_t idx = (uint8_t)((e->prev_state << 2) | new_state);
    int8_t delta = QDEC_TABLE[idx];

    if (delta != 0) {
        uint32_t status = save_and_disable_interrupts();
        e->pos += delta;
        restore_interrupts(status);
    }

    e->prev_state = new_state;
}

void encoder_init(encoder_t *e) {
    gpio_init(e->pin_a);
    gpio_set_dir(e->pin_a, GPIO_IN);

    gpio_init(e->pin_b);
    gpio_set_dir(e->pin_b, GPIO_IN);

    if (e->use_pullups) {
        gpio_pull_up(e->pin_a);
        gpio_pull_up(e->pin_b);
    }

    e->pos = 0;
    e->rot90 = 0;
    e->rot_accum = 0;
    e->last_pos_for_rot = 0;
    e->prev_state = encoder_read_state(e);

    gpio_to_encoder[e->pin_a] = e;
    gpio_to_encoder[e->pin_b] = e;

    if (!encoder_irq_callback_installed) {
        gpio_set_irq_enabled_with_callback(
            e->pin_a,
            GPIO_IRQ_EDGE_RISE | GPIO_IRQ_EDGE_FALL,
            true,
            &encoder_gpio_isr
        );
        encoder_irq_callback_installed = true;
    } else {
        gpio_set_irq_enabled(
            e->pin_a,
            GPIO_IRQ_EDGE_RISE | GPIO_IRQ_EDGE_FALL,
            true
        );
    }

    gpio_set_irq_enabled(
        e->pin_b,
        GPIO_IRQ_EDGE_RISE | GPIO_IRQ_EDGE_FALL,
        true
    );
}

int32_t encoder_get_position(const encoder_t *e) {
    uint32_t status = save_and_disable_interrupts();
    int32_t v = e->pos;
    restore_interrupts(status);
    return v;
}

void encoder_reset(encoder_t *e) {
    uint32_t status = save_and_disable_interrupts();
    e->pos = 0;
    e->rot90 = 0;
    e->rot_accum = 0;
    e->last_pos_for_rot = 0;
    restore_interrupts(status);
}

int32_t encoder_get_detents(const encoder_t *e, int32_t counts_per_detent) {
    if (counts_per_detent <= 0) {
        return 0;
    }
    return encoder_get_position(e) / counts_per_detent;
}

int32_t encoder_get_slot(encoder_t *e, int32_t counts_per_90, int32_t threshold) {
    if (counts_per_90 <= 0) return 0;
    if (threshold < 0) threshold = 0;

    uint32_t status = save_and_disable_interrupts();

    int32_t pos = e->pos;
    int32_t delta = pos - e->last_pos_for_rot;
    e->last_pos_for_rot = pos;

    e->rot_accum += delta;

    int32_t trigger = counts_per_90 - threshold;

    while (e->rot_accum >= trigger) {
        e->rot90 += 1;
        e->rot_accum -= counts_per_90;
    }

    while (e->rot_accum <= -trigger) {
        e->rot90 -= 1;
        e->rot_accum += counts_per_90;
    }

    int32_t out = e->rot90;
    restore_interrupts(status);
    return out;
}
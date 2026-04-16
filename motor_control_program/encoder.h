#ifndef ENCODER_H
#define ENCODER_H

#include <stdint.h>
#include <stdbool.h>

typedef struct {
    // config
    uint8_t pin_a;
    uint8_t pin_b;
    bool use_pullups;

    // runtime state
    volatile int32_t pos;
    volatile uint8_t prev_state;

    volatile int32_t rot90;
    volatile int32_t rot_accum;
    volatile int32_t last_pos_for_rot;
} encoder_t;

void encoder_init(encoder_t *e);
int32_t encoder_get_position(const encoder_t *e);
void encoder_reset(encoder_t *e);

int32_t encoder_get_detents(const encoder_t *e, int32_t counts_per_detent);
int32_t encoder_get_slot(encoder_t *e, int32_t counts_per_90, int32_t threshold);

#endif
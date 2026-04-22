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
    /* Each increment: valid quadrature transition (QDEC_TABLE delta != 0). */
    volatile uint32_t quad_valid_edges;

    volatile int32_t rot90;
    volatile int32_t rot_accum;
    volatile int32_t last_pos_for_rot;
} encoder_t;

void encoder_init(encoder_t *e);
int32_t encoder_get_position(const encoder_t *e);
uint32_t encoder_get_quad_edge_count(const encoder_t *e);
void encoder_reset(encoder_t *e);

int32_t encoder_get_detents(const encoder_t *e, int32_t counts_per_detent);
/* Integrated quadrature position (QDEC_TABLE in encoder.c) → slot index.
 * counts_per_slot: quadrature counts accumulated per one mechanical Geneva slot. */
int32_t encoder_get_slot(encoder_t *e, int32_t counts_per_slot, int32_t threshold);

#endif
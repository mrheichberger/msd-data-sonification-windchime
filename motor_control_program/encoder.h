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
    /* Snapshot at last slot index update (forward Geneva / one-way). */
    volatile uint32_t edges_at_slot_boundary;
    volatile int32_t pos_at_slot_boundary;
} encoder_t;

void encoder_init(encoder_t *e);
int32_t encoder_get_position(const encoder_t *e);
uint32_t encoder_get_quad_edge_count(const encoder_t *e);
void encoder_reset(encoder_t *e);

int32_t encoder_get_detents(const encoder_t *e, int32_t counts_per_detent);
/*
 * Slot index from valid quadrature edge count + stall detection.
 * counts_per_slot: reserved / unused for this algorithm (callers may pass legacy value).
 * threshold: max |delta pos| for "same number" stall rule (use 3–8 typical); if <= 0 uses 4.
 */
int32_t encoder_get_slot(encoder_t *e, int32_t counts_per_slot, int32_t threshold);

#endif

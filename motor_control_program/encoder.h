#ifndef ENCODER_H
#define ENCODER_H

#include <stdint.h>
#include <stdbool.h>

int32_t encoder_get_detents(int32_t counts_per_detent); //converts counts to detents

typedef struct {
    uint8_t pin_a;
    uint8_t pin_b;
    bool use_pullups;
} encoder_t;

void encoder_init(const encoder_t *e);
int32_t encoder_get_position(void);
void encoder_reset(void);

int32_t encoder_get_filtered_detents(int32_t counts_per_detent);
//function to increase dedent by 1 when the count amount increases by a number 
//in a threshold with hysterisis

//to get the number of 90 degree rotations
int32_t encoder_get_slot(int32_t counts_per_90, int32_t threshold);

#endif

//------------------------------------------------------------------------------
// encoder.c
// Encoder interface implementation for Raspberry Pi Pico
// May need ot add RC debounce later if noisy readings
//------------------------------------------------------------------------------

#include "encoder.h"
#include "pico/stdlib.h"
#include "hardware/sync.h"

// Global state (single encoder for now)
static volatile int32_t g_pos = 0; //encoder position to be modified in ISR
//do we have to worry about encoder rollover....?? modulus arithmetic?
static uint8_t g_pin_a = 0;
static uint8_t g_pin_b = 0;
static volatile uint8_t g_prev_state = 0; //prev state read in ISR
static volatile int32_t g_detents = 0;        // filtered detents (stable)
static volatile int32_t g_detent_accum = 0;   // accumulates raw count deltas
static volatile int32_t g_last_pos_for_det = 0;

//these globals to get hysterisis count to #90 rotations
static volatile int32_t g_rot90 = 0;
static volatile int32_t g_rot_accum = 0;
static volatile int32_t g_last_pos_for_rot = 0;



// Quadrature lookup table:
// index = (prev_state<<2) | new_state, where state is 2 bits: (A<<1)|B
// value = -1, 0, +1 per transition
// [2 bit prev][2 bit new] in binary -> decimal to spot in LUT = direction result 
static const int8_t QDEC_TABLE[16] = {
    0, -1, +1,  0,
   +1,  0,  0, -1,
   -1,  0,  0, +1,
    0, +1, -1,  0
};


//Read the current encoder state 
//Returns [A B] as 2-bit value
static inline uint8_t read_state(void) {
    // A is MSB, B is LSB
    uint8_t a = gpio_get(g_pin_a) ? 1 : 0;
    uint8_t b = gpio_get(g_pin_b) ? 1 : 0;
    return (uint8_t)((a << 1) | b);
}

int32_t encoder_get_detents(int32_t counts_per_detent) {
    if (counts_per_detent <= 0) return 0;
    return encoder_get_position() / counts_per_detent;  // integer division
}//convert counts to detents
//update this to increase a dendent everytime the amount of counts increases by a threshold amount

// GPIO interrupt service routine
static void encoder_gpio_isr(uint gpio, uint32_t events) {
    (void)gpio;
    (void)events;

    uint8_t new_state = read_state(); //get current state
    uint8_t idx = (uint8_t)((g_prev_state << 2) | new_state); //determine direction from LUT
    int8_t delta = QDEC_TABLE[idx]; 

    if (delta != 0) {
        // Make update atomic vs other interrupts
        uint32_t status = save_and_disable_interrupts();
        g_pos += delta;
        restore_interrupts(status);
    }

    g_prev_state = new_state; //update previous state with current state
}

//function to initalize the encoder at restart 
void encoder_init(const encoder_t *e) {
    g_pin_a = e->pin_a;
    g_pin_b = e->pin_b; //store pin numbers so IRS can access them

    gpio_init(g_pin_a);
    gpio_set_dir(g_pin_a, GPIO_IN);     //make pins inputs

    gpio_init(g_pin_b);
    gpio_set_dir(g_pin_b, GPIO_IN);

    if (e->use_pullups) {
        gpio_pull_up(g_pin_a);
        gpio_pull_up(g_pin_b);    //pull-ups if requested
    }

    // Initialize previous state so for good first transition 
    g_prev_state = read_state();
    g_pos = 0;

    //these are for the counting 90 degree rotations
    g_rot90 = 0;
    g_rot_accum = 0;
    g_last_pos_for_rot = 0;


    // Attach interrupts on BOTH pins, BOTH edges
    gpio_set_irq_enabled_with_callback(g_pin_a,
        GPIO_IRQ_EDGE_RISE | GPIO_IRQ_EDGE_FALL,
        true,
        &encoder_gpio_isr);

    gpio_set_irq_enabled(g_pin_b,
        GPIO_IRQ_EDGE_RISE | GPIO_IRQ_EDGE_FALL,
        true);
}


int32_t encoder_get_position(void) {
    // atomic read
    uint32_t status = save_and_disable_interrupts();
    int32_t v = g_pos;
    restore_interrupts(status);
    return v;
}

/* this will */
void encoder_reset(void) {
    uint32_t status = save_and_disable_interrupts();
    g_pos = 0;
    restore_interrupts(status);
}


/* this function determines how many slots in the geneva mechanism have been rotated through
we are using a threshold to say if the number of counts is large enough then 
count that as a rotation to account for any noise in the system 

inputs: the number of counts for one slot rotation, and then the number of 
counts that the position may be off by */

int32_t encoder_get_slot(int32_t counts_per_90, int32_t threshold) {
    if (counts_per_90 <= 0) return 0;
    if (threshold < 0) threshold = 0;

    uint32_t status = save_and_disable_interrupts();

    int32_t pos = g_pos;
    int32_t delta = pos - g_last_pos_for_rot;
    g_last_pos_for_rot = pos;

    g_rot_accum += delta;

    int32_t trigger = counts_per_90 - threshold;

    while (g_rot_accum >= trigger) {
        g_rot90 += 1;
        g_rot_accum -= counts_per_90;
    }
    while (g_rot_accum <= -trigger) {
        g_rot90 -= 1;
        g_rot_accum += counts_per_90;
    }

    int32_t out = g_rot90;
    restore_interrupts(status);
    return out;
}

/*
This file needs: 
-UART initialization
-code to read incoming serial data
-code to parse the incoming message
-code to transmit the encoder position back
*/

//UART prototpye 
//Created by Marinna Heichberger n 3/17/2026
//Goal is to read in the number of geneva slots it needs to move from pi
//Write back the number of geneva slots that actually moved

#include "uart_comm.h"
#include "pico/stdlib.h"
#include "hardware/uart.h"
#include "hardware/gpio.h"
#include <stdio.h>
#include <stdlib.h>

#define UART_ID uart0
#define BAUD_RATE 115200
#define UART_TX_PIN 16 //physical pin 21
#define UART_RX_PIN 17 //physical pin 22

#define BUF_SIZE 32

static char buffer[BUF_SIZE];
static int index = 0;

void uart_comm_init(void) {
    uart_init(UART_ID, BAUD_RATE);
    gpio_set_function(UART_TX_PIN, GPIO_FUNC_UART);
    gpio_set_function(UART_RX_PIN, GPIO_FUNC_UART);
}

bool uart_comm_read_int(int32_t *value) {
    while (uart_is_readable(UART_ID)) {
        char c = uart_getc(UART_ID);

        if (c == '\r') {
            continue;
        }

        if (c == '\n') {
            buffer[index] = '\0';
            *value = atoi(buffer);
            index = 0;
            return true;
        }

        if (index < BUF_SIZE - 1) {
            buffer[index++] = c;
        } else {
            index = 0;
        }
    }
    return false;
}

void uart_comm_send_int(int32_t value) {
    char msg[32];
    sprintf(msg, "%ld\n", (long)value);
    uart_puts(UART_ID, msg);
}
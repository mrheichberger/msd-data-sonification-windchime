//Header file for uart_comm.c 
//Created by Marinna Heichberger on 3/17/2026

#ifndef UART_COMM_H
#define UART_COMM_H

#include <stdbool.h>
#include <stdint.h>

void uart_comm_init(void);
bool uart_comm_read_int(int32_t *value);
void uart_comm_send_int(int32_t value);

#endif
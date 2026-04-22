cmake_minimum_required(VERSION 3.13)

include(pico_sdk_import.cmake)

project(motor_control_program_single_debug C CXX ASM)
pico_sdk_init()

add_executable(motor_control_program_single_debug
    main.c
    ../motor_control_program/motor_driver.c
    ../motor_control_program/encoder.c
    ../motor_control_program/uart_comm.c
)

# Print debugging over USB serial.
pico_enable_stdio_usb(motor_control_program_single_debug 1)
pico_enable_stdio_uart(motor_control_program_single_debug 0)

target_link_libraries(motor_control_program_single_debug
    pico_stdlib
    hardware_pwm
    hardware_uart
    hardware_gpio
)

pico_add_extra_outputs(motor_control_program_single_debug)

cmake_minimum_required(VERSION 3.13)

# Import the Pico SDK (uses PICO_SDK_PATH)
include(pico_sdk_import.cmake)

project(motor_control_program C CXX ASM)
pico_sdk_init()

add_executable(motor_control_program
    main.c
    motor_driver.c
    encoder.c
    uart_comm.c
)

# stdio over USB for printf debugging
pico_enable_stdio_usb(motor_control_program 1)
pico_enable_stdio_uart(motor_control_program 0)

target_link_libraries(motor_control_program
    pico_stdlib
    hardware_pwm
    hardware_uart
    hardware_gpio
    #pico_cyw43_arch_none   # for MAC address / Pico W chip access without lwIP
)

pico_add_extra_outputs(motor_control_program)
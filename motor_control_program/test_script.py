from uart_service import UARTComm

uart = UARTComm()

try:
    uart.connect()
    result = uart.move_motor_and_get_result(1, 3)
    print("Received result:", result)
except Exception as e:
    print("UART test error:", e)
finally:
    uart.close()
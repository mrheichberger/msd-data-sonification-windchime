#-------------------------------------------
#
# Created by Marinna Heichberger on 3/20/25
# Raspberry Pi 3 B UART service
# Sends:
#   1) motor number
#   2) requested slots
# Receives:
#   actual slots moved
#
#-------------------------------------------

import serial
import time


class UARTComm:
    def __init__(self, port="/dev/serial0", baudrate=115200, timeout=1):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None

    def connect(self):
        self.ser = serial.Serial(
            port=self.port,
            baudrate=self.baudrate,
            timeout=self.timeout
        )
        time.sleep(2)

    def send_move_command(self, motor_num: int, slots: int):
        if self.ser is None:
            raise RuntimeError("UART not connected")

        if not 1 <= motor_num <= 8:
            raise ValueError("motor_num must be between 1 and 8")

        motor_message = f"{motor_num}\n"
        slots_message = f"{slots}\n"

        self.ser.write(motor_message.encode("utf-8"))
        self.ser.write(slots_message.encode("utf-8"))

    def read_response(self) -> int:
        if self.ser is None:
            raise RuntimeError("UART not connected")

        response = self.ser.readline()
        print("Raw bytes:", response)

        decoded = response.decode("utf-8", errors="ignore").strip()

        if decoded == "":
            raise RuntimeError("No UART response received")

        return int(decoded)

    def move_motor_and_get_result(self, motor_num: int, slots: int) -> int:
        self.send_move_command(motor_num, slots)
        actual_slots_moved = self.read_response()
        return actual_slots_moved

    def close(self):
        if self.ser is not None and self.ser.is_open:
            self.ser.close()


if __name__ == "__main__":
    uart = UARTComm()

    try:
        uart.connect()

        motor_num = 1
        requested_slots = 3

        actual_slots_moved = uart.move_motor_and_get_result(
            motor_num,
            requested_slots
        )

        print(f"Motor {motor_num} requested {requested_slots} slots")
        print(f"Motor {motor_num} actually moved {actual_slots_moved} slots")

    except Exception as e:
        print("UART error:", e)

    finally:
        uart.close()

        '''
        #to use in other files
        # from uart_service import UARTComm

uart = UARTComm()
uart.connect()

actual = uart.move_motor_and_get_result(3, 5)
print(actual)

uart.close()
'''
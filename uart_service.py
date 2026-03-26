#-------------------------------------------
#
# Created by Marinna Heichberger on 3/20/25
# In order to communicate over UART 
# This is for Raspberry Pi 3 B in order
# to communcate with pi pico w 
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

    def send_slots(self, slots: int):
        if self.ser is None:
            raise RuntimeError("UART not connected")
        message = f"{slots}\n"
        self.ser.write(message.encode("utf-8"))

    def read_response(self):
        if self.ser is None:
            raise RuntimeError("UART not connected")
        response = self.ser.readline()
        print("Raw bytes:", response)
        return response.decode("utf-8", errors="ignore").strip()

    def close(self):
        if self.ser is not None and self.ser.is_open:
            self.ser.close()


if __name__ == "__main__":
    uart = UARTComm()

    try:
        uart.connect()
        uart.send_slots(3)
        reply = uart.read_response()
        print("Received:", reply)
    except Exception as e:
        print("UART error:", e)
    finally:
        uart.close()

from machine import UART
import pycom
import machine
import os

print("Booting...")
# Disable heartbeat
pycom.heartbeat(False)

uart = UART(0, baudrate=115200)
os.dupterm(uart)

print("Booting Complete!")
print("Executing: main.py")
machine.main('main.py')
# This script is for receiving data from the Xbox controller
# Joystick values must be scaled 0-20000 for DShot

# spidev will only install on Linux host, like the Pi
import time
import struct
import sys
import spidev
import pygame as p

# Scale the -1 to 1 float (must fit within 2 bytes unsigned int)
NUM_RESOLUTION = 10000

p.init()
p.joystick.init()

spi = spidev.SpiDev()
# Pi's bus 0, CS 0 (GPIO8 / pin 24 on Pi)
spi.open(0, 0)
# Initialize SPI at 500KHz
spi.max_speed_hz = 500_000
# Idle low
spi.mode = 0

# Format data for SPI transfer
def send_spi(x, y, z):
    # Most significant byte first, with 2 signed ints
    data = struct.pack(">hhh", x, y, z)
    # Sends 4 values of bytes as a list
    spi.xfer2(list(data))

# If no controls are active
if p.joystick.get_count() == 0:
    print("No gamepad detected")
    controller_state = False
    sys.exit(1)

# Otherwise, assume controller is ready
else:
    js = p.joystick.Joystick(0)
    js.init()
    print(f"Controller connected: {js.get_name()}")
    num_axes = js.get_numaxes()
    num_buttons = js.get_numbuttons()
    controller_state = True


print(f"Num axes: {num_axes}\nNum buttons: {num_buttons}")

error_counter = 0

try:
    while (controller_state):
        # Pull events each frame, so OS doesn't mark unresponsive
        p.event.pump()

        try:
            """
            Extra caution to not send negative ints,
            though ints over 20000 would be handled in STM code 
            and will send over SPI without issue.
            """

            # Side-to-side motion -- unsigned int -- left stick
            side = int(max((js.get_axis(0) + 1) * NUM_RESOLUTION, 0))
            # Forwad-back motion -- unsigned int -- left stick
            front = int(max((js.get_axis(1) + 1) * NUM_RESOLUTION, 0))
            # Vertical motion -- unsigned int -- right stick
            vertical = int(max((js.get_axis(4) + 1) * NUM_RESOLUTION, 0))

            send_spi(side, front, vertical)

            error_counter = 0

            time.sleep(0.01)

        except p.error as e:
            error_counter += 1
            if (error_counter > 9):
                controller_state = False
                print(f"Unexpected consecutive errors occurred: {str(e)}")

            # Error recovery time
            time.sleep(0.2)
        
except KeyboardInterrupt:
    print("Program ended by user")

finally:
    spi.close()
    p.close()
    sys.exit(0)
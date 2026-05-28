"""
This script is for receiving data from the Xbox controller
Joystick values must be scaled 0-20,000 for vertical motion,
-10,000 to 10,000 for 2D planar motion
Left stick for 2D planar motion, right stick for elevation
"""

# Important note: Vertical will be at 10,000 when controller is at rest
# Positive values for back and left, negative for front and right


import time
import struct
import sys
import spidev # spidev will only install on Linux host, like the Pi
import pygame as p

# Scaling and clamping
NUM_RESOLUTION = 10000
MIN_INPUT = 500
MAX_HORIZONTAL_INPUT = 10000
MAX_VERTICAL_INPUT = 20000
DISARM_VALUE = -30000
ARM_VALUE = 30000
# Joysticks
LATERAL_AXIS = 0
LONGITUDE_AXIS = 1
VERTICAL_AXIS = 3
# Buttons
DISARM_BUTTON = 0
ARM_BUTTON = 1


# Fits data inside int16
def clamp(v, lo, hi): 
    return lo if v < lo else hi if v > hi else v

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
    # Most significant byte first, with 3 signed ints
    data = struct.pack(">hhh", x, y, z)
    # Sends 4 values of bytes as a list
    spi.xfer2(list(data))

def send_command(value):
    send_spi(value, value, value)

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
            # Side-to-side motion -- signed int -- left stick
            side = int(js.get_axis(LATERAL_AXIS) * NUM_RESOLUTION)
            # Forward-back motion -- signed int -- left stick
            front = int(js.get_axis(LONGITUDE_AXIS) * NUM_RESOLUTION)
            # Vertical motion -- signed int -- right stick
            vertical = int((1 - js.get_axis(VERTICAL_AXIS)) * NUM_RESOLUTION)
            # Disarm button (A)
            disarm = js.get_button(DISARM_BUTTON)
            # Arm button (B)
            arm = js.get_button(ARM_BUTTON)

            if disarm:
                send_command(DISARM_VALUE)
            elif arm:
                send_command(ARM_VALUE)
            else:
                # Clamp stick drift around center
                if -MIN_INPUT < side < MIN_INPUT:
                    side = 0

                # Clamp stick drift around center
                if -MIN_INPUT < front < MIN_INPUT:
                    front = 0

                # Clamp stick drift around hover/rest value
                if (NUM_RESOLUTION - MIN_INPUT) < vertical < (NUM_RESOLUTION + MIN_INPUT):
                    vertical = NUM_RESOLUTION

                side = clamp(side, -MAX_HORIZONTAL_INPUT, MAX_HORIZONTAL_INPUT)
                front = clamp(front, -MAX_HORIZONTAL_INPUT, MAX_HORIZONTAL_INPUT)
                vertical = clamp(vertical, 0, MAX_VERTICAL_INPUT)

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
    p.quit()
    sys.exit(0)

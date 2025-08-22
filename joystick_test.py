"""
This script is for testing the script and Xbox controller
Joystick values must be scaled 0-20,000 for vertical motion,
-10,000 to 10,000 for 2D planar motion
Left stick for 2D planar motion, right stick for elevation
"""

# Important note: Vertical will be at 10,000 when controller is at rest
# Positive values for back and left, negative for front and right

import time
import sys
import pygame as p

# Scale the -1 to 1 float
NUM_RESOLUTION = 10000
# We can adjust as needed
MIN_INPUT = 500

# To ensure we send data that fits in int16
def clamp(v, lo, hi): 
    return lo if v < lo else hi if v > hi else v

p.init()
p.joystick.init()

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
            side = int(js.get_axis(0) * NUM_RESOLUTION)
            # Forward-back motion -- signed int -- left stick
            front = int(js.get_axis(1) * NUM_RESOLUTION)
            # Vertical motion -- unsigned int -- right stick
            vertical = int((1 - js.get_axis(3)) * NUM_RESOLUTION)

            # -10,000 to 10,000
            if -MIN_INPUT < side < MIN_INPUT:
                side = 0

            # -10,000 to 10,000
            if -MIN_INPUT < front < MIN_INPUT:
                front = 0

            # 0 to 20,000
            if (10000 - MIN_INPUT) < vertical < (10000 + MIN_INPUT):
                vertical = 10000

            side = clamp(side, -10000, 10000)
            front = clamp(front, -10000, 10000)
            vertical = clamp(vertical, 0, 20000)

            print(f"Side (x): {side}, Forward (y): {front}, Vertical (z): {vertical}")

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
    p.quit()
    sys.exit(0)
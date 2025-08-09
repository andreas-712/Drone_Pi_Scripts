"""
This script is for testing the script and Xbox controller
Joystick values must be scaled 0-20,000
Left stick for 2D planar motion, right stick for elevation
"""

"""
Important note: side-to-side, forward-back, vertical will be at 10,000 when controller is at rest
We must make sure this is accounted for in STM code before being taken at absolute value in the STM
"""

import time
import sys
import pygame as p

# Scale the -1 to 1 float (must fit within 2 bytes unsigned int)
NUM_RESOLUTION = 10000

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

            # Side-to-side motion -- unsigned int -- left stick
            side = int(max((js.get_axis(0) + 1) * NUM_RESOLUTION, 0))
            # Forward-back motion -- unsigned int -- left stick
            front = int(max((js.get_axis(1) + 1) * NUM_RESOLUTION, 0))
            # Vertical motion -- unsigned int -- right stick
            vertical = int(max((js.get_axis(4) + 1) * NUM_RESOLUTION, 0))

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
    spi.close()
    p.close()
    sys.exit(0)
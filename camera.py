'''
This script will run the camera (Pi camera 3)
and run the TFLite model in near real time
Installs on the Pi (not through requirements.txt):
python3-picamera2, python3-opencv
'''

from picamera2 import Picamera2
from libcamera import Transform
import cv2
import numpy as np
import time, sys

# Initialize camera
camera = Picamera2()

# Size is pixel resolution
# YUV420 skips colour unnecessary colour conversion, saving memory
video_config = camera.create_video_configuration(
    # Main feed for display
    main = {"size": (1280, 720), "format": "YUV420"},
    # Low resolution stream for fast ML inference time
    lores = {"size": (352, 352), "format": "YUV420"},
    # No flipping feed over any axis
    transform = Transform(vflip = False, hflip = False)
)

# Configure camera
camera.configure(video_config)
camera.start()
time.sleep(0.2)

# Set up far-focus and lock it in (using AF to find the best point)
try:
    camera.set_controls({"AfMode": 1, "AfTrigger": 1})
    time.sleep(0.5)
    camera.set_controls({"AfMode": 1})
except Exception:
    pass

try:
    while True:
        # Capture low res frames (feeds into TF model)
        yuv_lores = camera.capture_array("lores")
        # Convert to RGB after reducing resolution for efficiency
        rgb_lores = cv2.cvtColor(yuv_lores, cv2.COLOR_YUV420p2RGB)

        # Captures main display to stream
        yuv_main = camera.capture_array("main")
        # Displayed stream expects BGR, not RGB format
        bgr_main = cv2.cvtColor(yuv_main, cv2.COLOR_YUV420p2BGR)
        cv2.imshow("Preview", bgr_main)

        # Exit method for OpenCV
        if cv2.waitKey(1) & 0xFF == 27:
            break

# Exit with Ctrl + C
except KeyboardInterrupt:
    print("Stream interrupted by user")

# Catch any other errors
except Exception as e:
    print(f"Error occurred: {e}")

# Close stream at end of program
finally:
    try:
        camera.stop()
    except Exception:
        pass
    cv2.destroyAllWindows()
    sys.exit(0)
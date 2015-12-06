"""
This module implements auto-detection of the Raspberry Pi and chooses the best
camera based on the auto-detection.
"""

__author__ = "Ron Wright"
__copyright__ = "Copyright 2015 Ronald Joseph Wright"
__maintainer__ = "Ron Wright"

# Try to determine whether we are on Raspberry Pi.
IS_RASPBERRY_PI = False
try:
    with open('/proc/cpuinfo', 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('Hardware') and \
               (line.endswith('BCM2708') or line.endswith('BCM2709')):
                IS_RASPBERRY_PI = True
                break
except:
    pass

# If this script is running on the Raspberry Pi, use the CSI port.  Otherwise,
# use standard operations.
if IS_RASPBERRY_PI:
    from pi_camera import ThePiCamera
    class AutoCamera(ThePiCamera):
        pass
else:
    from generic_camera import GenericCamera
    class AutoCamera(GenericCamera):
        pass

"""
This module implements camera frame retrieval, used for object avoidance, for
Raspberry Pi cameras. The implementation is based on information at
http://www.pyimagesearch.com/2015/03/30/accessing-the-raspberry-pi-camera-with-opencv-and-python/.
"""

__author__ = "Ron Wright"
__copyright__ = "Copyright 2015 Ronald Joseph Wright"
__maintainer__ = "Ron Wright"

from camera import Camera
from picamera.camera import PiCamera
from picamera.array import PiRGBArray
import time

class ThePiCamera(Camera):
    """
    Class for Raspberry Pi camera frame retrieval.
    """
    def __init__(self):
        """
        Constructor for ThePiCamera. This initializes parameters for Raspberry
        Pi camera capture.
        """
        self.camera = PiCamera()
        self.camera.resolution = (640, 480)
        self.camera.framerate = 32
        self.rawCapture = PiRGBArray(self.camera, size=(640, 480))
        time.sleep(0.1) # allow the camera to warm up

    def get_iterator(self):
        """
        Returns an iterator for obtaining a continuous stream of camera frames.
        """
        return self.camera.capture_continuous(self.rawCapture, format='bgr', use_video_port=True)

    def get_frame(self, raw_frame):
        """
        Retrieves the camera frame returned by the iterator, converted into a
        2D array.
        """
        array = raw_frame.array
        self.rawCapture.truncate(0)
        return array

    def destroy(self):
        """
        Cleans up memory used for Raspberry Pi camera capture.
        """
        self.camera.close()

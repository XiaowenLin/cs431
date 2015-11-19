"""
This module implements camera frame retrieval, used for object avoidance, for
any camera supported by OpenCV.
"""

__author__ = "Ron Wright"
__copyright__ = "Copyright 2015 Ronald Joseph Wright"
__maintainer__ = "Ron Wright"

from camera import Camera
import cv2

class GenericCameraIterator:
    """
    Iterator class for GenericCamera. This is used to obtain a continuous
    stream of camera frames.
    """
    def __init__(self, cap):
        """
        Constructor for GenericCameraIterator.
        """
        self.cap = cap

    def __iter__(self):
        """
        Return a reference to the iterator, which is the GenericCameraIterator
        class itself.
        """
        return self

    # Iterate and grab frames indefinitely
    def next(self):
        """
        Retrieves the next frame and returns it.
        """
        _, frame = self.cap.read()
        return frame

class GenericCamera(Camera):
    """
    Class for camera frame retrieval.
    """
    def __init__(self):
        """
        Constructor for GenericCamera. This initializes OpenCV camera capture.
        """
        self.cap = cv2.VideoCapture(0)

    def get_iterator(self):
        """
        Returns the iterator GenericCameraIterator.
        """
        return GenericCameraIterator(self.cap)

    def get_frame(self, raw_frame):
        """
        Retrieves the camera frame, which is already in a 2D array format, so
        it just returns the frame returned by the iterator.
        """
        return raw_frame

    def destroy(self):
        """
        Cleans up memory used for OpenCV camera capture.
        """
        self.cap.release()

"""
This module contains the base class for camera frame retrieval, which is used
for obstacle avoidance.
"""

__author__ = "Ron Wright"
__copyright__ = "Copyright 2015 Ronald Joseph Wright"
__maintainer__ = "Ron Wright"

class Camera:
    """
    Abstract class for camera frame retrieval.
    """
    def __init__(self):
        """
        Constructor for Camera.
        """
        pass

    def get_iterator(self):
        """
        Abstract function for retrieving an iterator for obtaining a continuous
        stream of camera frames.
        """
        pass

    def get_frame(self, raw_frame):
        """
        Abstract function that converts a raw frame into a frame that can be
        used as a 2D array.
        """
        pass

    def destroy(self):
        """
        Abstract function that cleans up memory after use of the class.
        """
        pass

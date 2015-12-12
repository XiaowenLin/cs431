"""
This module implements a client that receives frames from a frame server.
"""

__author__ = "Ron Wright"
__copyright__ = "Copyright 2015 Ronald Joseph Wright"
__maintainer__ = "Ron Wright"

import socket, socket_util
import numpy as np
import cv2

class FrameClient:
    """
    Class for receiving frames from a frame server
    """
    def __init__(self, host, port=11111):
        """
        Constructor for FrameClient, where host is the hostname or IP address
        of the frame server, and the optional parameter port (with default
        value 11111) is the port number of the frame server.
        """
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))
    
    def get_frame(self):
        """
        Retrieves the frame data from the server and converts it into a
        representation understandable by OpenCV, which is returned by the
        function. In the case of an error, None is returned.
        """
        message = socket_util.recv_msg(self.s)
        if message is None:
            return None
        return cv2.imdecode(np.fromstring(message, dtype=np.uint8), 1)

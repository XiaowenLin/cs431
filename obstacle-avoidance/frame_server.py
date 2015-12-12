"""
This module implements a server that sends frames to connected clients in
real time.
"""

__author__ = "Ron Wright"
__copyright__ = "Copyright 2015 Ronald Joseph Wright"
__maintainer__ = "Ron Wright"

from push_server import PushServer
import cv2

class FrameServer(PushServer):
    """
    Class for sending image frames to clients in real time
    """
    def __init__(self, port=11111, backlog=5):
        """
        Constructor for FrameServer, where the optional parameter port (with
        default value 11111) is the port number to use for the frame server,
        and the optional parameter backlog (with default value 5) is the
        maximum number of incoming client connections that can wait between
        successive accept calls.
        """
        super(FrameServer, self).__init__(port, backlog)

    def push_frame(self, the_frame):
        """
        Sets the frame to be sent to connected clients. Clients are notified
        only when the frame is valid.
        """
        ret_val, buf = cv2.imencode('.jpg', the_frame)
        if ret_val:
            super(FrameServer, self).push_message(buf.tostring())

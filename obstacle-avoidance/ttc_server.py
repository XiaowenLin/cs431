"""
This module implements a server that sends TTC values to connected clients in
real time.
"""

__author__ = "Ron Wright"
__copyright__ = "Copyright 2015 Ronald Joseph Wright"
__maintainer__ = "Ron Wright"

from push_server import PushServer
import socket_util
from math import isinf

class TTCServer(PushServer):
    """
    Class for sending TTC values to clients in real time
    """
    def __init__(self, port=22222, backlog=5):
        """
        Constructor for TTCServer, where the optional parameter port (with
        default value 22222) is the port number to use for the TTC server,
        and the optional parameter backlog (with default value 5) is the
        maximum number of incoming client connections that can wait between
        successive accept calls.
        """
        super(TTCServer, self).__init__(port, backlog, True)

    @staticmethod
    def sanitize_number(number):
        """
        Helper function that converts any infinity value into the string
        'Infinity'. This function should not be used outside of this class.
        """
        return 'Infinity' if isinf(number) else number

    def push_ttc_values(self, min_ttc, left_ttc, right_ttc):
        """
        Sets the frame to be sent to connected clients. Clients are notified
        only when the frame is valid.
        """
        super(TTCServer, self).push_message(\
            {'min-ttc': TTCServer.sanitize_number(min_ttc), \
             'left-ttc': TTCServer.sanitize_number(left_ttc), \
             'right-ttc': TTCServer.sanitize_number(right_ttc)})

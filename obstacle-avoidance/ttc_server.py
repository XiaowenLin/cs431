"""
This module implements a server that sends TTC values to connected clients in
real time.
"""

__author__ = "Ron Wright"
__copyright__ = "Copyright 2015 Ronald Joseph Wright"
__maintainer__ = "Ron Wright"

from push_server import PushServer
import socket_util
import json

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
        super(TTCServer, self).__init__(port, backlog)

    def push_ttc_values(self, min_ttc, left_ttc, right_ttc):
        """
        Sets the frame to be sent to connected clients. Clients are notified
        only when the frame is valid.
        """
        ttc_json_data = json.dumps({'min-ttc': min_ttc, \
                                    'left-ttc': left_ttc, \
                                    'right-ttc': right_ttc})
        super(TTCServer, self).push_message(ttc_json_data)

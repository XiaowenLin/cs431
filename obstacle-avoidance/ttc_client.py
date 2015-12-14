"""
This module implements a client that receives TTC values from a TTC server.
"""

__author__ = "Ron Wright"
__copyright__ = "Copyright 2015 Ronald Joseph Wright"
__maintainer__ = "Ron Wright"

import socket, socket_util

class TTCClient:
    """
    Class for receiving TTC values from a TTC server
    """
    def __init__(self, host, port=22222):
        """
        Constructor for TTCClient, where host is the hostname or IP address of
        the TTC server, and the optional parameter port (with default value
        22222) is the port number of the frame server.
        """
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))
    
    def get_ttc_values(self):
        """
        Retrieves the TTC values from the server and returns them as a triple.
        In the case of an error, None is returned.
        """
        return socket_util.recv_msg_as_json(self.s)

    def shutdown(self):
        """
        Shuts down the TTC client.
        """
        self.s.shutdown(socket.SHUT_RDWR)

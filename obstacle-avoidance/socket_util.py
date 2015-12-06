"""
This module contains functions that make sending large amounts of data over a
socket connection easier. The code was taken from
http://stackoverflow.com/questions/17667903.
"""

__author__ = "Ron Wright"
__copyright__ = "Copyright 2015 Ronald Joseph Wright"
__maintainer__ = "Ron Wright"

import struct

def send_msg(sock, msg):
    """
    Prefixes the message msg with a 4-byte length (in network byte order) and
    sends it using the socket sock.
    """
    msg = struct.pack('>I', len(msg)) + msg
    sock.sendall(msg)

def recv_msg(sock):
    """
    Reads the data from the socket sock. First, it reads the 4-byte message
    length, and then it reads the message data accordingly. This function
    returns the received bytes (without the 4-byte header), or None if EOF is
    hit.
    """
    # Read message length and unpack it into an integer
    raw_msglen = recvall(sock, 4)
    if not raw_msglen:
        return None
    msglen = struct.unpack('>I', raw_msglen)[0]
    # Read the message data
    return recvall(sock, msglen)

def recvall(sock, n):
    """
    Helper function to recv n bytes, or return None if EOF is HIT. This
    function should not be used directly outside this module.
    """
    data = ''
    while len(data) < n:
        packet = sock.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data

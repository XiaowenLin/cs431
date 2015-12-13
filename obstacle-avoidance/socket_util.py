"""
This module contains functions that make sending large amounts of data over a
socket connection easier. The code was taken from
http://stackoverflow.com/questions/17667903.
"""

__author__ = "Ron Wright"
__copyright__ = "Copyright 2015 Ronald Joseph Wright"
__maintainer__ = "Ron Wright"

import struct
from math import isinf

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

def float_to_bytes(value):
    """
    Converts the given float value into bytes consisting of a 32-byte integer
    and a 32-bit fraction (both in network byte, or big endian, order). The
    first byte is 0x01 if the value is infinite and 0x00 if the value is
    finite.

    If the given value is finite, it will return the following:

        +---+----------------+-----------------+
        | 0 | 32-bit integer | 32-bit fraction |
        +---+----------------+-----------------+

    If the given value is infinite, it will return the following:

        +---+----------------------------------+
        | 1 |    64 bits (8-bytes) of zeros    |
        +---+----------------------------------+

    """
    if isinf(value):
        return '\1' + 8*'\0'
    integer_part = int(value)
    fractional_part = int((value - integer_part) * 4294967296.0)
    return '\0' + struct.pack('>I', integer_part) \
                + struct.pack('>I', fractional_part)

def bytes_to_float(the_bytes):
    """
    Converts the string of bytes given by the_bytes (with a 32-byte integer
    and a 32-bit fraction) into a float value. This function is essentially the
    inverse of float_to_bytes.
    """
    if len(the_bytes) == 9:
        is_infinite_byte = the_bytes[0]
        if is_infinite_byte == '\0':
            integer_part = struct.unpack('>I', the_bytes[1:5])[0]
            fractional_part = struct.unpack('>I', the_bytes[5:])[0]
            return integer_part + (fractional_part / 4294967296.0)
        return float('inf')
    return None

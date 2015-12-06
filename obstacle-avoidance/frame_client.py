import socket
from socket_util import SocketUtil
import numpy as np
import cv2

class FrameClient:
    def __init__(self, host, port=12345):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))
    
    def get_frame(self):
        message = SocketUtil.recv_msg(self.s)
        if message is None:
            return None
        return cv2.imdecode(np.fromstring(message, dtype=np.uint8), 1)

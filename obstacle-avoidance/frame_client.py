import socket
from socket_util import SocketUtil

class FrameClient:
    def __init__(self, host, port=12345):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((host, port))
    
    def get_frame(self):
        return SocketUtil.recv_msg(self.s)
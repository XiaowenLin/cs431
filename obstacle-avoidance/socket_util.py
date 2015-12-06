import struct
import numpy as np
import cv2

class SocketUtil:
    @staticmethod
    def send_msg(sock, msg):
        msg = struct.pack('>I', len(msg)) + msg
        sock.sendall(msg)
    
    @staticmethod
    def recv_msg(sock):
        raw_msglen = SocketUtil.recvall(sock, 4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        # Read the message data
        return SocketUtil.recvall(sock, msglen)
    
    @staticmethod
    def recvall(sock, n):
        # Helper function to recv n bytes or return None if EOF is HIT
        data = ''
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    @staticmethod
    def get_raw_image_buffer(np_image):
        _, buf = cv2.imencode('.jpg', np_image)
        return buf.astype(np.uint8).tostring()

    @staticmethod
    def get_image_from_raw_buffer(buf):
        return cv2.imdecode(np.fromstring(buf, dtype=np.uint8), 1)

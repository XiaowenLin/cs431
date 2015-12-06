import socket
from socket_util import SocketUtil
from threading import Condition
import threading
import numpy as np
import cv2

class FrameServer:
    def __init__(self, port=12345, backlog=5):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('', port))
        self.s.listen(backlog)
        self.frame_as_jpeg_bytes = None
        self.seq_number = 0
        self.cv = Condition()

    def set_frame(self, the_frame):
        _, buf = cv2.imencode('.jpg', the_frame)
        frame_as_jpeg_bytes = buf.tostring()

        self.cv.acquire()
        self.frame_as_jpeg_bytes = frame_as_jpeg_bytes
        self.seq_number += 1
        self.cv.notifyAll()
        self.cv.release()

    def handle_request(self, conn, addr):
        conn_closed = False
        old_seq_number = 0
        while not conn_closed:
            self.cv.acquire()
            while old_seq_number == self.seq_number:
                self.cv.wait()
            frame_as_jpeg_bytes = self.frame_as_jpeg_bytes
            old_seq_number = self.seq_number
            self.cv.release()
            try:
                SocketUtil.send_msg(conn, frame_as_jpeg_bytes)
            except socket.error:
                conn_closed = True

    def continuously_check_for_new_connections(self):
        while True:
            conn, addr = self.s.accept()
            t = threading.Thread(target=self.handle_request, args=(conn, addr))
            t.daemon = True
            t.start()

    def run_daemon_thread(self):
        t = threading.Thread(target=self.continuously_check_for_new_connections)
        t.daemon = True
        t.start()

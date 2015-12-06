"""
This module implements a server that sends frames to connected clients in
real time.
"""

__author__ = "Ron Wright"
__copyright__ = "Copyright 2015 Ronald Joseph Wright"
__maintainer__ = "Ron Wright"

import socket, socket_util
from threading import Condition
import threading
import numpy as np
import cv2

class FrameServer:
    """
    Class for sending image frames to clients in real time
    """
    def __init__(self, port=12345, backlog=5):
        """
        Constructor for FrameServer, where the optional parameter port (with
        default value 12345) is the port number to use for the frame server,
        and the optional parameter backlog (with default value 5) is the
        maximum number of incoming client connections that can wait between
        successive accept calls.
        """
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('', port))
        self.s.listen(backlog)
        self.frame_as_jpeg_bytes = None
        self.seq_number = 0
        self.cv = Condition()

    def set_frame(self, the_frame):
        """
        Sets the frame to be sent to connected clients. Clients are notified
        only when the frame is valid.
        """
        ret_val, buf = cv2.imencode('.jpg', the_frame)
        if ret_val:
            frame_as_jpeg_bytes = buf.tostring()
            self.cv.acquire()
            self.frame_as_jpeg_bytes = frame_as_jpeg_bytes
            self.seq_number += 1
            self.cv.notifyAll()
            self.cv.release()

    def handle_request(self, conn, addr):
        """
        Client session function that sends frames to the client in real time.
        This function should not be used directly outside this class.
        """
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
                socket_util.send_msg(conn, frame_as_jpeg_bytes)
            except socket.error:
                conn_closed = True

    def continuously_check_for_new_connections(self):
        """
        Service function for accepting incoming client connections. A session
        thread is allocated for each connection. This function should not be
        used directly outside this class.
        """
        while True:
            conn, addr = self.s.accept()
            t = threading.Thread(target=self.handle_request, args=(conn, addr))
            t.daemon = True
            t.start()

    def run_daemon_thread(self):
        """
        Starts the frame server thread.
        """
        t = threading.Thread(target=self.continuously_check_for_new_connections)
        t.daemon = True
        t.start()

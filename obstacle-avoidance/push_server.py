"""
This module implements a server that sends messages to connected clients in
real time.
"""

__author__ = "Ron Wright"
__copyright__ = "Copyright 2015 Ronald Joseph Wright"
__maintainer__ = "Ron Wright"

import socket, socket_util
from threading import Condition
import threading

class PushServer(object):
    """
    Class for sending messages to clients in real time
    """
    def __init__(self, port, backlog=5):
        """
        Constructor for PushServer, where port is the port number to use for
        the push server, and the optional parameter backlog (with default
        value 5) is the maximum number of incoming client connections that can
        wait between successive accept calls.
        """
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('', port))
        self.s.listen(backlog)
        self.message_to_push = None
        self.seq_number = 0
        self.cv = Condition()

    def push_message(self, message):
        """
        Sets the message to be sent to connected clients.
        """
        self.cv.acquire()
        self.message_to_push = message
        self.seq_number += 1
        self.cv.notifyAll()
        self.cv.release()

    def handle_request(self, conn, addr):
        """
        Client session function that sends messages to the client in real time.
        This function should not be used directly outside this class.
        """
        conn_closed = False
        old_seq_number = 0
        while not conn_closed:
            self.cv.acquire()
            while old_seq_number == self.seq_number:
                self.cv.wait()
            message_to_push = self.message_to_push
            old_seq_number = self.seq_number
            self.cv.release()
            try:
                socket_util.send_msg(conn, message_to_push)
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
        Starts the push server thread.
        """
        t = threading.Thread(target=self.continuously_check_for_new_connections)
        t.daemon = True
        t.start()

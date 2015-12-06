import socket
from socket_util import SocketUtil
from threading import Condition
import threading

class FrameServer:
    def __init__(self, port=12345, backlog=5):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind(('', port))
        self.s.listen(backlog)
        self.the_frame = None
        self.cv = Condition()
    
    def set_frame(self, the_frame):
        self.cv.acquire()
        self.the_frame = the_frame
        self.cv.notifyAll()
        self.cv.release()
    
    def handle_request(self, conn, addr):
        conn_closed = False
        while not conn_closed:
            self.cv.acquire()
            while self.the_frame is None:
                self.cv.wait()
            try:
                SocketUtil.send_msg(conn, self.the_frame)
            except socket.error:
                conn_closed = True
            self.the_frame = None
            self.cv.release()
        
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
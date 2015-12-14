#!/usr/bin/python           # This is client.py file
"""
client.py runs on control end to communicate with server on beagle board. 
features:
1. send movement messages through socket
   get feedback info
   {'topic': 'coordinates',
              'origin': (0, 0),
              'destination': (1, 1)}
2. send command for vedio streaming through socket from control device
   send vedio streaming to assigned destination

"""
from __init__ import *
import json
import socket
import threading

class Commander:
    def __init__(self):
        # create a socket object
        self.s = socket.socket()
        self.s.connect((TCP_HOST, TCP_PORT))

    def send_worker(self, msg_s):
        t = threading.Thread(target=self.send_msg, args=(msg_s, ))
        t.start()

    def send_msg(self, msg_s):
       """
       >>> msg = {'topic': 'coordinates',
                  'origin': (0, 0),
                  'destination': (1, 1)}
       >>> msg_s = json.dumps(msg)
       >>> send_msg(msg_s)
       200
       """
       self.s.send(msg_s)
       logging.info('waiting for server response')
       recv_s = s.recv(BUFFER_SIZE)
       recv = json.loads(recv_s)
       if recv:
           logging.debug(recv['status'])
           logging.info('finish sending')
           return recv
       else:
           return

    def close(self):
        for t in threading.enumerate():
            if t is main_thread:
                continue
                logging.debug('joining %s', t.getName())
                t.join()
            self.s.close                     # Close the socket when done
        logging.debug('close success')

if __name__ == '__main__':
    msg = {'topic': 'coordinates',
           'origin': (0, 0),
           'destination': (1, 1)}
    msg_s = json.dumps(msg)
    cmd = Commander()
    cmd.send_worker(msg_s)
    cmd.close()

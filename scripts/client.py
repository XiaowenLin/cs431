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

class Commander:
    def __init__(self):
        # create a socket object
        self.s = socket.socket()
        self.s.connect((TCP_HOST, TCP_PORT))

    def send_msg(self, msg_s):
       """
       >>> msg = {'topic': 'coordinates',
                  'origin': (0, 0),
                  'destination': (1, 1)}
       >>> msg_s = json.dumps(msg)
       >>> send_msg(msg_s)
       200
       """
       s.send(msg_s)
       # recv_s = s.recv(BUFFER_SIZE)
       # recv = json.loads(recv_s)
       # logging.debug(recv['status'])
       # return recv
       logging.info('finish sending')
       return

    def close(self):
        self.s.close                     # Close the socket when done

if __name__ == '__main__':
    msg = {'topic': 'coordinates',
           'origin': (0, 0),
           'destination': (1, 1)}
    msg_s = json.dumps(msg)
    cmd = Commander()
    cmd.send_msg(msg_s)
    cmd.close()

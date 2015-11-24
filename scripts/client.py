#!/usr/bin/python           # This is client.py file
"""
client.py runs on control end to communicate with server on beagle board. 
features:
1. send movement messages through socket
   get feedback info
2. send command for vedio streaming through socket from control device
   send vedio streaming to assigned destination
"""
import json
from __init__ import *
import socket               

# create a socket object
s = socket.socket()         
s.connect((TCP_HOST, TCP_PORT))

msg = {'topic': 'instruction',
       'instruction': '145 0 0 0'}
msg_s = json.dumps(msg)
s.send(msg_s)
recv_s = s.recv(BUFFER_SIZE)
recv = json.loads(recv_s)
print recv['status']
s.close                     # Close the socket when done

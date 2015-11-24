#!/usr/bin/python           # This is server.py file
"""
server.py runs on beagle board to control roomba. 
features:
1. receive movement messages through socket from control device
   send feedback info to control device
2. receive command for vedio streaming through socket from control device
   send vedio streaming to assigned destination
"""
import json
from __init__ import *
import socket               # Import socket module

# define messages
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         # Create a socket object
s.bind((TCP_HOST, TCP_PORT))        # Bind to the port
s.listen(5)                 # Now wait for client connection. 5 is the number of backlog

msg = {'status': 200}
msg_s = json.dumps(msg)
conn, addr = s.accept()
print 'connection address:', addr
while 1:
    data = conn.recv(BUFFER_SIZE)
    if not data: break
    print "received data:", data
    conn.send(msg_s)  # echo
conn.close()

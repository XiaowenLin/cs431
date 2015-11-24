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
import threading


class Server:
   ok_msg_s = json.dumps( {'status': 200} )
   total_request = 0
   count_lock = threading.Lock()
   def __init__(self, backlog=5):
       self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         # Create a socket object
       self.s.bind((TCP_HOST, TCP_PORT))                                  # Bind to the port
       self.s.listen(backlog)                                             # Now wait for client connection. 

   def handle_request(self, conn, addr):
       Server.count_lock.acquire()
       Server.total_request += 1
       logging.debug('total request = %d', Server.total_request)
       Server.count_lock.release()
       print 'connection address:', addr
       data = conn.recv(BUFFER_SIZE)
       if not data: return
       logging.debug("received data: %s", data)
       #TODO: do something based on data
       conn.send(Server.ok_msg_s)  # echo
       conn.close()
       return

if __name__ == '__main__':
    server = Server()
    threads = []
    while True:
        conn, addr = server.s.accept()
        t = threading.Thread(target=server.handle_request, args=(conn, addr))
        t.start()
        

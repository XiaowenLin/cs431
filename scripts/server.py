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
from robot import Robot
from exceptions import KeyError


class Server:
    ok_msg_s = json.dumps({'status': 200})
    fail_msg_s = json.dumps({'status': 400})
    total_request = 0

    def __init__(self, backlog=5):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         # Create a socket object
        self.s.bind((TCP_HOST, TCP_PORT))                                  # Bind to the port
        self.s.listen(backlog)                                             # Now wait for client connection.
        self.actions = {'coordinates': self._move_robot}
        self.roomba = Robot()


    def _execute(self, data):
        topic = data.get('topic')
        func = self.actions.get(topic)
        ret_msg = func(data)
        return ret_msg


    def handle_request(self, conn, addr):
        Server.total_request += 1
        logging.debug('total request = %d', Server.total_request)
        print 'connection address:', addr
        data = conn.recv(BUFFER_SIZE)
        if not data:
            conn.send(Server.fail_msg_s)  # echo
            return
        logging.debug("received data: %s", data)
        data = json.loads(data)
        status_s = self._execute(data)
        conn.send(status_s)  # echo
        conn.close()
        return

    def _move_robot(self, data):
        try:
            origin = data['origin']
            destination = data['destination']
            return self.roomba.navigate(origin, destination)
        except KeyError:
            logging.debug("Bad data with missing keys.")
            return json.dumps({'status': 400})

if __name__ == '__main__':
    server = Server()
    while True:
        conn, addr = server.s.accept()
        server.handle_request(conn, addr)


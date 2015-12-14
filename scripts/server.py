#!/usr/bin/python           # This is server.py file
"""
server.py runs on beagle board to control roomba. 
features:
1. receive movement messages through socket from control device
   send feedback info to control device
2. receive command for vedio streaming through socket from control device
   send vedio streaming to assigned destination

json string to control:
{'topic': 'coordinates', 'origin': [0, 0], 'destination': [1, 1]}
{'topic': 'angle', 'turn': 90.0}
{'topic': 'stop'}
{'topic': 'forward'}
"""
import json
from __init__ import *
import socket               # Import socket module
from robot import Robot
from exceptions import KeyError
import threading


class Server:
    ok_msg_s = json.dumps({'status': 200})
    fail_msg_s = json.dumps({'status': 400})
    total_request = 0
    count_lock = threading.Lock()
    roomba_lock = threading.Lock()

    def __init__(self, backlog=5):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         # Create a socket object
        self.s.bind((TCP_HOST, TCP_PORT))                                  # Bind to the port
        self.s.listen(backlog)                                             # Now wait for client connection.
        self.actions = {'coordinates': self._move_robot,                   # Add new actions here
                        'angle': self._turn_robot,
                        'stop': self._stop_robot,
                        'forward': self._forward_robot,
			'backward': self._backward_robot}
        self.roomba = Robot()


    def _execute(self, data):
        topic = data.get('topic')
        func = self.actions.get(topic)
        ret_msg = func(data)
        return ret_msg


    def handle_request(self, conn, addr):
        """
        increase the number of total requests
        ask roomba to stop
        then send new command
        :param conn:
        :param addr:
        :return:
        """
        Server.count_lock.acquire()
        Server.total_request += 1
        logging.debug('total request = %d', Server.total_request)
        Server.count_lock.release()
        logging.info('connection address: %s', addr)
        data = conn.recv(BUFFER_SIZE)
        if not data:
            conn.send(Server.fail_msg_s)  # echo
            return
        logging.debug('received data: %s', data)
        data = json.loads(data)
        #Server.roomba_lock.acquire()
        #self.roomba.stop()
        #Server.roomba_lock.release()
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

    def _turn_robot(self, data):
        """
        turn the robot only
        :param data: float
        :return: serilized json
        """
        return self.roomba.turn(data.get('turn'))

    def _stop_robot(self, data):
        """
        stop robot
        :param data:
        :return:
        """
        return json.dumps({'status': 200})

    def _forward_robot(self, data):
        return self.roomba.forward()

    def _backward_robot(self, data):
        return self.roomba.backward()

    def dummy(self):
        return 0


if __name__ == '__main__':
    server = Server()
    t= threading.Thread(target=server.dummy)
    t.start()
    while True:
        logging.debug('listening')
        conn, addr = server.s.accept()
        server.roomba.stop()
        t.join()
        logging.debug('previous thread finished')
        server.roomba.app.stop = False
        t = threading.Thread(target=server.handle_request, args=(conn, addr))
        t.start()

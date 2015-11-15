import sys
from rtbot_blank import *

from sys import stdin
from rtbot_blank import *
import logging
import time
import SocketServer
import socket
import threading
import Queue
import signal

HOST = ''
PORT = 50000

FORMAT = '%(asctime)s %(levelname)s [%(filename)s:%(lineno)d] %(message)s'
DATE_FORMAT = '%H%M%S'

def turn(robot, degrees, velocity, direction, sleep_interval=.01):    
    robot.sensors.GetAngle()
    robot.TurnInPlace(velocity, direction) 
    degrees_turned = 0
    while ((direction == 'ccw' and degrees_turned < degrees) or
          (direction == 'cw' and (-1 * degrees_turned) < degrees)):
        degrees_turned += robot.sensors.GetAngle()
        time.sleep(sleep_interval)
    robot.Stop()
    return degrees_turned

def forward(robot, distance, velocity, sleep_interval=.01):
    robot.sensors.GetDistance()
    robot.DriveStraight(velocity)
    distance_traveled = 0
    while ((velocity > 0 and distance_traveled < distance) or
           (velocity < 0 and distance_traveled > distance)):
        distance_traveled += robot.sensors.GetDistance()
        time.sleep(sleep_interval)
    robot.Stop()
    return distance_traveled


def main():
    logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt=DATE_FORMAT)
    global robot
    robot = Rtbot(sys.argv[1])
    robot.start()
    robot.DriveStraight(1)
    
        
if __name__ == '__main__':
  main()

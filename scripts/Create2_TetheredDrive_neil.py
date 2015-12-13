#!/usr/bin/env python
# -*- coding: utf-8 -*-
# 27 May 2015

###########################################################################
# Copyright (c) 2015 iRobot Corporation
# http://www.irobot.com/
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
#   Redistributions of source code must retain the above copyright
#   notice, this list of conditions and the following disclaimer.
#
#   Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in
#   the documentation and/or other materials provided with the
#   distribution.
#
#   Neither the name of iRobot Corporation nor the names
#   of its contributors may be used to endorse or promote products
#   derived from this software without specific prior written
#   permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
###########################################################################
from __init__ import *
import struct
import sys, glob # for listing serial ports
import time
import math
from threading import Thread
try:
    import serial
except ImportError:
    raise


VELOCITYCHANGE = 200
ROTATIONCHANGE = 300

TIMEOUT =1000
TIME = .05
VEL = 100
VEL_H = 200
VEL_TH = 200
ROT = 30

ITERMAX = 3
DETOUR = 50
DETOURMAX = 50
DANGLE = 90
DANGLEMAX = 90
BACK = 5
AGG = 50
ERR =50

class Command():

    def __init__(self, name, value):
        self.name = name
        self.value = value

    def getName(self):
        return self.name

    def getValue(self):
        return self.value	

class TetheredDriveApp():

    def __init__(self):
        self.connection = None
        self.stop = False
        self.motions = {'UP': Command('UP', -VELOCITYCHANGE), 'DW': Command('DOWN', VELOCITYCHANGE), 'RT': Command('RIGHT', -ROTATIONCHANGE), 'LT': Command('LEFT', ROTATIONCHANGE)}
        self.commands = {'P': Command('PASSIVE', '128'), 'S': Command('SAFE', '131'), 'F': Command('FULL', '132'), 'C': Command('CLEAN', '135'), 'D': Command('DOCK', '143'), 'R': Command('RESET', '7'), 'B': Command('BEEP', '140 3 1 64 16 141 3')}
        self.assists = {'PTS': Command('PORTS', lambda: self.getSerialPorts()), 'Q': Command('QUIT', lambda: self.doQuit()), 'H': Command('HELP', lambda: self.getHelp()), 'CT': Command('CONNECT', lambda: self.doConnect())}

    def getAssistCommands(self):
        return self.assists
        
    # sendCommandASCII takes a string of whitespace-separated, ASCII-encoded base 10 values to send
    def sendCommandASCII(self, command):
        cmd = ""
        for v in command.split():
            cmd += chr(int(v))

        self.sendCommandRaw(cmd)

    # sendCommandRaw takes a string interpreted as a byte array
    def sendCommandRaw(self, command):

        try:
            if self.connection is not None:
                self.connection.write(command)
            else:
                print( "Not connected.")
        except serial.SerialException:
            print( "Lost connection")
            self.connection = None

        print( ' '.join([ str(ord(c)) for c in command ]) )
        print( '\n')

    # getDecodedBytes returns a n-byte value decoded using a format string.
    # Whether it blocks is based on how the connection was set up.
    def getDecodedBytes(self, n, fmt):
        
        try:
            return struct.unpack(fmt, self.connection.read(n))[0]
        except serial.SerialException:
            print( 'Uh-oh', "Lost connection to the robot!")
            self.connection = None
            return None
        except struct.error:
            print( "Got unexpected data from serial port.")
            return None

    # get8Unsigned returns an 8-bit unsigned value.
    def get8Unsigned(self):
        return self.getDecodedBytes(1, "B")

    # get8Signed returns an 8-bit signed value.
    def get8Signed(self):
        return self.getDecodedBytes(1, "b")

    # get16Unsigned returns a 16-bit unsigned value.
    def get16Unsigned(self):
        return self.getDecodedBytes(2, ">H")
    
    # get16Signed returns a 16-bit signed value.
    def get16Signed(self):
        return self.getDecodedBytes(2, ">h")

    # A handler for keyboard events. Feel free to add more!
    def sendKey(self, key):

        if (key in ['P', 'S', 'F', 'C', 'D', 'B', 'R']):
            self.sendCommandASCII(self.commands[key].getValue())
        elif (key == 'EM'):  # END MOVEMENT
            self.sendDriveCommand(0,0)    
        elif key in ['UP', 'DW']: #UP & DOWN
            self.sendDriveCommand( self.motions[key].getValue(),0)
        elif key in ['LT', 'RT']: #LEFT & RIGHT
            self.sendDriveCommand(0, self.motions[key].getValue())
    def senseBUMP (self):
        self.sendCommandASCII ('142 45') #sense wall
        wall = self.getDecodedBytes(1, ">B")
        #print( "Wall : ", wall)
        return wall
    def senseWALL (self):
        self.sendCommandASCII ('142 8') #sense wall
        wall = self.getDecodedBytes(1, ">B")
        #print( "Wall : ", wall)
        return wall
    def doGo2(self, num): 
        self.sendCommandASCII ('142 19') #sense distance
        distance = self.getDecodedBytes(2, ">h")
        distance = 0
        set_distance = float(num)
        watchdog =0
        cnt =0
        if set_distance>0 :
            direction =1
        else:
            direction =-1
        #print( distance, ' ', watchdog)
        if (set_distance  > VEL_TH):
            #print( 'high speed')
            speed = direction *VEL_H
        else:
            speed = direction *VEL
        cmd = struct.pack(">Bhh", 145, speed, speed)
        self.sendCommandRaw(cmd)
        while (distance < (direction *set_distance) and watchdog != TIMEOUT and not self.stop):
            if (set_distance * direction - distance < VEL_TH):
                if (speed*direction <= VEL):
                    speed = direction *VEL
                else:
                    speed -= AGG*direction 
            cmd = struct.pack(">Bhh", 145, speed, speed)
            self.sendCommandRaw(cmd)
        
            if (direction==1 and self.senseBUMP()):
                print( '>>>>A Wall Ahead')
                cmd = struct.pack(">Bhh", 145, 0, 0)
                self.sendCommandRaw(cmd)
                return float(num) - distance
            time.sleep(TIME)
            self.sendCommandASCII ('142 19')
            read = self.getDecodedBytes(2, ">h")
            distance -= read*direction
            #print( distance, ' ', direction*set_distance, ' ', watchdog)
            watchdog+=1            
            if read == 0:
                cnt+=1
            if cnt==3 :
                watchdog = TIMEOUT
        cmd = struct.pack(">Bhh", 145, 0, 0)
        self.sendCommandRaw(cmd)
        return 0
    def doLEFT(self):
        cmd = struct.pack(">Bhh", 145, ROT, (-1 * ROT))
        self.sendCommandRaw(cmd)
        time.sleep(TIME)
        cmd = struct.pack(">Bhh", 145, 0, 0)
        self.sendCommandRaw(cmd)    
    def doRIGHT(self):
        cmd = struct.pack(">Bhh", 145, -1 *ROT, (1 * ROT))
        self.sendCommandRaw(cmd)
        time.sleep(TIME)
        cmd = struct.pack(">Bhh", 145, 0, 0)
        self.sendCommandRaw(cmd)    
    def doUP(self):
        cmd = struct.pack(">Bhh", 145, VEL, VEL)
        self.sendCommandRaw(cmd)
        time.sleep(TIME)
        cmd = struct.pack(">Bhh", 145, 0, 0)
        self.sendCommandRaw(cmd)    
    def doSTOP(self):
        self.stop = True
        time.sleep(TIME*5)
        cmd = struct.pack(">Bhh", 145, 0, 0)
        self.sendCommandRaw(cmd)
        #self.stop = False
        
    def doTurn(self, num):
        self.sendCommandASCII ('142 20') #sense angle
        angle = self.getDecodedBytes(2, ">h")
        angle = 0
        set_angle = float(num)      
        watchdog =0
        cnt =0
        if set_angle >0 :
            direction =1
        else:
            direction =-1
        #print( angle, ' ', set_angle, ' ', watchdog)
        cmd = struct.pack(">Bhh", 145, direction*ROT, direction*(-1 * ROT))
        self.sendCommandRaw(cmd)
        while ((angle < direction*set_angle) and watchdog != TIMEOUT and not self.stop):
            time.sleep(TIME)
            self.sendCommandASCII ('142 20')
            read = 2.1 *self.getDecodedBytes(2, ">h")
            angle += direction*read
            #print(  angle, ' ',set_angle, ' ', watchdog)
            watchdog+=1
            #if read == 0:
            #    cnt +=1
            #if cnt == 3:
            #    watchdog = TIMEOUT
        cmd = struct.pack(">Bhh", 145, 0, 0)
        self.sendCommandRaw(cmd)
        return 0

    def doSenseLoop(self):
        while(1):
            time.sleep(TIME)
            read =self.senseBUMP()
                    
        
    
    def doNav2(self, direction, x, y, x_set, y_set):
         x_offset =100 * ( x_set - x)
         y_offset =100 * (y_set - y)
     
         if (x_offset <0 ):
             x_dir = -1
         else:
             x_dir = 1
             
             
         if (y_offset):
             angle =    180 / math.pi * math.atan(x_offset/y_offset)
             if (angle <0 ):
                 angle = -90 - angle
             else:
                 angle = 90 - angle
             if (x_dir == -1):
                 angle -= 180
         elif (x_offset <0 ):
             angle = -180
         else:
             angle = 0
             
         angle -= direction
         
         if (angle > 180):
             angle = 360 -angle
         elif angle < -180:
             angle += 360
             
         distance  = (x_offset**2 + y_offset**2 )**0.5
         #print( 'TURN ', angle, ', THEN GO ', distance)
         self.doTurn(angle)
         
         remain =self.doGo2(distance)
         sum_angle =0
         navdog = 0
         
         while (remain >ERR and navdog < ITERMAX and not self.stop):
             navdog+= 1
             #print( 'Remaining distance', remain)
             if (self.senseWALL()):
                 print( "HIT A WALL")
                 self.doSOUND()
                 return remain
             wall = self.senseBUMP();

             if (wall):
                 back = BACK - self.doGo2 (-BACK)
                 remain += back
 
             if (wall & 2  and wall &32): #stucked
                 myangle = -DANGLE
                 back = BACK - self.doGo2 (-BACK) #extra back
                 remain += back
             elif (wall & 3):# turn right
                 myangle = -DANGLE
             else: #turn left
                 myangle = DANGLE
                 
             self.doTurn( myangle)
             sum_angle += myangle

             wall = self.senseBUMP();
             if (wall ): #still wall ahead, keep turning
                 print( "Keep turning ...")
                 break
                
             detour =  DETOUR - self.doGo2 (DETOUR)


          #   X = remain - detour* math.cos(sum_angle)
          #   Y = detour * math.sin (sum_angle)
          #   angle = -90 + sum_angle + math.atan(X/Y)
             
             #angle =  (myangle/DANGLE)*180 * math.atan (detour/remain) /math.pi  + myangle
             angle =  -(myangle/DANGLE) * (180 - 180 / math.pi * math.atan(remain/detour))
             print( 'New angle', angle)
             if (angle > 180):
                 angle = 360 -angle
             elif angle < -180:
                 angle += 360
             self.doTurn( angle)
             sum_angle += angle   
             distance  = (remain**2 + 50**2 )**0.5
         #    distance = (X**2 + Y**2) ** 0.5
             print( 'New Distance', distance)
             remain = self.doGo2 (distance)
         self.doTurn(-sum_angle)
         self.doSOUND()
         return remain       
         
  
    def doSOUND(self):
#        cmd = struct.pack(">BBBBB", 140,  0, 1, 60, 32)
#        self.sendCommandRaw(cmd)

        cmd = struct.pack(">BB", 141,  0)
        self.sendCommandRaw(cmd)


    def sendDriveCommand(self, velocity, rotation): 
    	# compute left and right wheel velocities
        vr = velocity + (rotation/2)
        vl = velocity - (rotation/2)

        # create drive command
        cmd = struct.pack(">Bhh", 145, vr, vl)
        self.sendCommandRaw(cmd)

    def doConnectFromServer(self, port='/dev/ttyUSB0'):
        if self.connection is not None:
            print( "Oops, You're already connected!")
            return 0
            
        try:
            self.connection = serial.Serial(port, baudrate=115200, timeout=1)
            print( "Connected, Connection succeeded!")
            return 0
        except:
            print( "Failed, Sorry, couldn't connect to " + str(port) )
            return -1
            
        
    def doConnect(self):
 
        if self.connection is not None:
            print( "Oops, You're already connected!")
            return

        try:
            ports = self.getSerialPorts()
            
            port = raw_input('Available COM Ports:\n' + '\n'.join(ports) + '\n Enter a COM Port: ' )
        except EnvironmentError:
            port = raw_input('Enter COM port to open: ')

        if port is not None:
            print( "Trying " + str(port) + "... " )
            try:
                self.connection = serial.Serial(port, baudrate=115200, timeout=1)
                print( "Connected, Connection succeeded!")
            except:
                print( "Failed, Sorry, couldn't connect to " + str(port) )


    def getHelp(self):
        print( '\nHelp \n')
        print( 'Operation Commands: \n')
        for key, value in self.commands.iteritems():
            print( key + " \t " + value.getName())
        print( "\n"    )

        print( 'Movement Commands: \n')
        for key, value in self.motions.iteritems():
            print( key + " \t " + value.getName())
        print( "\n")

        print( 'Assist Commands: \n')
        for key, value in self.assists.iteritems():
            print( key + " \t " + value.getName())
        print( "\n"  )  

    def doQuit(self):
        if (raw_input('Are you sure you want to quit? ') == 'YES'):
            if self.connection:
                self.sendKey('P')
            quit()

    def getSerialPorts(self):
        """Lists serial ports
        From http://stackoverflow.com/questions/12090503/listing-available-com-ports-with-python

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of available serial ports
        """
        if sys.platform.startswith('win'):
            ports = ['COM' + str(i + 1) for i in range(256)]

        elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
            # this is to exclude your current terminal "/dev/tty"
            ports = glob.glob('/dev/tty[A-Za-z]*')

        elif sys.platform.startswith('darwin'):
            ports = glob.glob('/dev/tty.*')

        else:
            raise EnvironmentError('Unsupported platform')

        result = []
        for port in ports:
            try:
                s = serial.Serial(port)
                s.close()
                result.append(port)
            except (OSError, serial.SerialException):
                pass

        if (result == ''):
        	result = "No ports found"

        return result    

class Main():

    def __init__(self):
        app = TetheredDriveApp()
        self.assists = app.getAssistCommands()
        
        while(True):
            key = raw_input("Enter a key: ")
            keys =key.split(' ')

            if key in ['H', 'PTS', 'Q', 'CT']:
                self.assists[key].getValue()()
            elif (keys[0] == 'GO'):
                app.doGo2(keys[1])
            elif (keys[0] == 'TURN'):
                app.doTurn(keys[1])
                #r = Thread(target=app.doTurn, args=[key[1]])
                #r.start()
            elif (keys[0] == 'NAV'):
                app.doNav2(float(keys[1]), float(keys[2]), float(keys[3]), float(keys[4]), float(keys[5]))
                #p = Thread(target=app.doNav2, args=[float(keys[1]), float(keys[2]), float(keys[3]), float(keys[4]), float(keys[5])])
                #p.start()
            elif (keys[0] == 'STOP'):
                q = Thread(target=app.doSTOP)
                q.start()
                q.join()
            elif (keys[0] == 'BUMP'):
                app.doSenseLoop()
            elif (keys[0] == 'SOUND'):
                app.doSOUND()
            
            else:    
            	app.sendKey(key)
        

if __name__ == "__main__":
    main = Main()

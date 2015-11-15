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

import struct
import sys, glob # for listing serial ports

try:
    import serial
except ImportError:
    raise

connection = None

VELOCITYCHANGE = 200
ROTATIONCHANGE = 300

helpText = """\

Supported Commands:

PASSIVE
SAFE
FULL
CLEAN
DOCK
RESET
UP
DOWN
RIGHT
LEFT
"""

class TetheredDriveApp():

    def __init__(self):
        self.callbackKeyDown = False
        self.callbackKeyUp = False
        self.callbackKeyLeft = False
        self.callbackKeyRight = False
        self.lastDriveCommand = ''

    # sendCommandASCII takes a string of whitespace-separated, ASCII-encoded base 10 values to send
    def sendCommandASCII(self, command):
        cmd = ""
        for v in command.split():
            cmd += chr(int(v))

        self.sendCommandRaw(cmd)

    # sendCommandRaw takes a string interpreted as a byte array
    def sendCommandRaw(self, command):
        global connection

        try:
            if connection is not None:
                connection.write(command)
            else:
                print "Not connected."
        except serial.SerialException:
            print "Lost connection"
            connection = None

        print ' '.join([ str(ord(c)) for c in command ])
        print ' '.join([ str(ord(c)) for c in command ])
        print '\n'

    # getDecodedBytes returns a n-byte value decoded using a format string.
    # Whether it blocks is based on how the connection was set up.
    def getDecodedBytes(self, n, fmt):
        global connection
        
        try:
            return struct.unpack(fmt, connection.read(n))[0]
        except serial.SerialException:
            print 'Uh-oh', "Lost connection to the robot!"
            connection = None
            return None
        except struct.error:
            print "Got unexpected data from serial port."
            return None

    # get8Unsigned returns an 8-bit unsigned value.
    def get8Unsigned(self):
        return getDecodedBytes(1, "B")

    # get8Signed returns an 8-bit signed value.
    def get8Signed(self):
        return getDecodedBytes(1, "b")

    # get16Unsigned returns a 16-bit unsigned value.
    def get16Unsigned(self):
        return getDecodedBytes(2, ">H")

    # get16Signed returns a 16-bit signed value.
    def get16Signed(self):
        return getDecodedBytes(2, ">h")

    # A handler for keyboard events. Feel free to add more!
    def sendKey(self, k):

        motionChange = False
        stop = False

        if (k == 'STOP'):  # Stop
            cmd = struct.pack(">Bhh", 145, 0, 0)
            self.sendCommandRaw(cmd)
            print 'Sending STOP Command \n'
        elif k == 'PASSIVE':   # Passive
            self.sendCommandASCII('128')
        elif k == 'SAFE': # Safe
            self.sendCommandASCII('131')
        elif k == 'FULL': # Full
            self.sendCommandASCII('132')
        elif k == 'CLEAN': # Clean
            self.sendCommandASCII('135')
        elif k == 'DOCK': # Dock
            self.sendCommandASCII('143')
        elif k == 'SPACE': # Beep
            self.sendCommandASCII('140 3 1 64 16 141 3')
        elif k == 'RESET': # Reset
            self.sendCommandASCII('7')
        elif k == 'UP':
            self.callbackKeyUp = True
            motionChange = True
        elif k == 'DOWN':
            self.callbackKeyDown = True
            motionChange = True
        elif k == 'LEFT':
            self.callbackKeyLeft = True
            motionChange = True
        elif k == 'RIGHT':
            self.callbackKeyRight = True
            motionChange = True
        else:
            print repr(k), "not handled"

        if motionChange == True:

            velocity = 0

            if self.callbackKeyUp is True:
                velocity += VELOCITYCHANGE
                self.callbackKeyUp = False
            else:
                velocity += 0

            if self.callbackKeyDown is True:
                velocity -= VELOCITYCHANGE
            else:
                velocity += 0
            
            rotation = 0

            if self.callbackKeyLeft is True:
                rotation += ROTATIONCHANGE
                self.callbackKeyLeft = False
            else:
                rotation += 0

            if self.callbackKeyRight is True:
                rotation -= ROTATIONCHANGE
                self.callbackKeyRight = False
            else:
                rotation -= 0
                
            # compute left and right wheel velocities
            vr = velocity + (rotation/2)
            vl = velocity - (rotation/2)

            # create drive command
            cmd = struct.pack(">Bhh", 145, vr, vl)
            self.sendCommandRaw(cmd)

    def doConnect(self):
        global connection

        if connection is not None:
            print 'Oops', "You're already connected!"
            return

        try:
            ports = self.getSerialPorts()
            
            port = raw_input('Available COM Ports:\n' + '\n'.join(ports) + '\n Enter a COM Port: ' )
        except EnvironmentError:
            port = raw_input('Enter COM port to open: ')

        if port is not None:
            print "Trying " + str(port) + "... "
            try:
                connection = serial.Serial(port, baudrate=115200, timeout=1)
                print 'Connected', "Connection succeeded!"
            except:
                print 'Failed', "Sorry, couldn't connect to " + str(port)


    def getHelp(self):
        print 'Help \n'
        print helpText

    def doQuit(self):
        if (raw_input('Are you sure you want to quit? ') == 'YES'):
            return True
        else:
            return False

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
        
        while(True):
            key = raw_input("Enter a key: ")
            if (key == 'HELP'):
                app.getHelp()
            elif (key == 'PORTS'):
                app.getSerialPorts()
            elif (key == 'QUIT'):
                if (app.doQuit() == True):
                    app.sendKey('PASSIVE')
                    return
            elif (key == 'CONNECT'):
                app.doConnect()
            else:    
            	app.sendKey(key)
        

if __name__ == "__main__":
    main = Main()

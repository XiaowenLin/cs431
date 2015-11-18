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
    def sendKey(self, key):

        if (key in ['P', 'S', 'F', 'C', 'D', 'B', 'R']):
            self.sendCommandASCII(self.commands[key].getValue())
        elif (key == 'EM'):  # END MOVEMENT
            self.sendDriveCommand(0,0)    
        elif key in ['UP', 'DW']: #UP & DOWN
            self.sendDriveCommand(0, self.motions[key].getValue())
        elif key in ['LT', 'RT']: #LEFT & RIGHT
            self.sendDriveCommand(self.motions[key].getValue(), 0)


    def sendDriveCommand(self, velocity, rotation): 
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
        print '\nHelp \n'
        print 'Operation Commands: \n'
        for key, value in self.commands.iteritems():
            print key + " \t " + value.getName()
        print "\n"    

        print 'Movement Commands: \n'
        for key, value in self.motions.iteritems():
            print key + " \t " + value.getName()
        print "\n"

        print 'Assist Commands: \n'
        for key, value in self.assists.iteritems():
            print key + " \t " + value.getName()
        print "\n"    

    def doQuit(self):
        if (raw_input('Are you sure you want to quit? ') == 'YES'):
            if connection:
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

            if key in ['H', 'PTS', 'Q', 'CT']:
                self.assists[key].getValue()()
            else:    
            	app.sendKey(key)
        

if __name__ == "__main__":
    main = Main()

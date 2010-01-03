#!/usr/bin/env python
# -*- coding: utf-8 -*-

#***************************************************************************
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU General Public License as published by  *
#*   the Free Software Foundation; either version 3 of the License, or     *
#*   (at your option) any later version.                                   *
#*                                                                         *
#***************************************************************************

"""
    This module is responsible for the communication with the LWZ heat pump.
    Currently it is only able to query the heat pump and can therefore not 
    write options. This is by design do not damage the LWZ.
    
    Written by Robert Penz <robert@penz.name>
"""

import serial
import struct
import sys

# normally no need to change it
serialTimeout = 5

## protocol constants
# common
STARTCOMMUNICATION = "\x02"
ESCAPE = "\x10"
BEGIN = "\x01\x00"
END = "\x03"

# query constants
GETVERSION = {"name": "getVersion",  "request": "\xfe\xfd"}
GETACTUALVALUES = {"name": "getActualValues",  "request": "\xfc\xfb"}

# name, position, fixedDecimals
actualValuesFloatPositions = (
        # don't know some
        ("flow temperature",6,1),
        ("return temperature",8,1),
        ("hot gas temperature",10,1),
        ("DHW temperature",12,1),
        ("flow temperature HC2",14,1),
        ("inside temperature",16,1),
        ("evaporator temperature",18,1),
        ("condenser temperature",20,1),
        # don't know 22-23,24
        ("extractor speed set",25,1),
        ("ventilator speed set",27,1),
        ("expelled air speed set",29,1),
        ("extractor speed actual",31,0),
        ("ventilator speed actual",33,0),
        ("expelled air speed actual",35,0),
        ("outside temperature",37,1),
        ("relative humidity",39,1),
        ("dew point temperature",41,1)
        # don't know some
    )


def convert2Float(s, fixedDecimals=1):
    if len(s) != 2:
        raise ValueError, "need excactly 2 bytes for float conversion"
    l = struct.unpack(">h",s)
    if fixedDecimals == 0:
        return l[0]
    else:
        return l[0]/10.0**fixedDecimals

def printHex(s):
    print "debug: ", 
    i = 0
    for t in s:
        if i % 4 == 0:
            print "| %d:" % i,  
        print "%02x" % ord(t),
        i += 1
    print "|"
    sys.stdout.flush()

def _calcChecksum(s):
    """ Internal function that calcuates the checksum """
    checksum = 1
    for i in xrange(0, len(s)):
        checksum += ord(s[i])
        checksum &= 0xFF
    return chr(checksum)

def verifyChecksum(s):
   """ verify if the provided string contains a valid checksum returns True if the checksum matches """
   if len(s) < 2:
       raise ValueError, "The provided string needs to be atleast 2 bytes long"
   return s[0] == _calcChecksum(s[1:])

def addChecksum(s):
    """ inserts a the beginning a checksum """
    if len(s) < 1:
        raise ValueError, "The provided string needs to be atleast 1 byte long"    
    return (_calcChecksum(s) + s)

class Protocol:
    # The device we talk to
    _serialDevice = None
    _debug = None
    
    # The object which does the serial talking
    _ser = None

    def __init__(self, serialDevice="/dev/ttyS0", debug = False):
        self._serialDevice = serialDevice
        self._debug = debug


    def _establishConnection(self):
        """ opens the serial connection and makes a "ping" to check if the 
            heat pump is responding 
        """
        if self._ser:
            raise IOError, "Error: serial connection already open"
        
        # open the serial connection
        self._ser = serial.Serial(self._serialDevice, timeout=serialTimeout)

        # check if the heat pump is connected and responds
        self._ser.write(STARTCOMMUNICATION)
        s = self._ser.read(1)
        if s != ESCAPE:
            raise IOError, "Error: heat pump does not respond - is it connected?"


    def _closeConnection(self):
        """ just closes the connection """
        if self._ser:
            self._ser.close()
            self._ser = None
    
    def _get(self, consts):
        """ internal method which does the real quering - provide it with a dict
            of the query protocol and it will handle the rest
        """
        if not self._ser:
            raise IOError, "Error: serial connection not open"
        # request the data
        self._ser.write(BEGIN + consts["request"] + ESCAPE + END)
        s = self._ser.read(2)
        if s != ESCAPE + STARTCOMMUNICATION:
            raise IOError, "Error: heat pump does not understand %s request" % consts["name"]
        
        # ready to receive data
        self._ser.write(ESCAPE)
        
        # we read data until we get the END flag, but not if the END flag is not escaped
        s = ""
        escaping = False
        while 1:
            tmp = self._ser.read(1)
            if not tmp:
                raise IOError, "Error: data stream brocken during %s reponse" % consts["name"]
        
            if len(s) < 2: # first 2 chars should be the header
                s += tmp
                if len(s) == 2 and s != BEGIN:
                    raise IOError, "Error: wrong response header for %s request" % consts["name"]
            else:
                if escaping:
                    if tmp == END: # special handling
                        break # we just stop reading
                    elif tmp == ESCAPE: # just add the char as it got escaped
                        s += tmp
                        escaping = False
                    else:
                        raise IOError, "Error: some char (%02x) got escaped which should not in %s request" % (ord(tmp), consts["name"])                    
                elif tmp == ESCAPE: # this char is used for escaping
                    escaping = True # do add nothing
                else: # normal, just add the char
                    s += tmp

        # extract the payload
        payload = s[len(BEGIN):].replace("\x2b\x18", "\x2b") # don't really know why, but it seems necessary
        
        # all worked, now we need to reset the connection in a state we can talk again
        self._ser.write(ESCAPE + STARTCOMMUNICATION)
        s = self._ser.read(1)
        if s != ESCAPE:
            printHex(s)
            raise IOError, "Error: could not be set again into receiving mode (%s)" % consts["name"]
        
        # for debugging
        if self._debug:
            printHex(payload)
        
        return payload
    
    def _getVersion(self):
        """ extracts the version of the heat pump software """
        # I don't know what the first 2 bytes mean
        return convert2Float(self._get(GETVERSION)[2:], 2)
    
    def _getActualValues(self):
        """ extracts the most important values with on query """
        s = self._get(GETACTUALVALUES)
        result = {}
        # hack until I find the reason for this problem
        if len(s) != 55:
            print "Warning: input is not 55 chars long"
            sys.stdout.flush()
        else:
            for entry in actualValuesFloatPositions:
                result[entry[0]] =  convert2Float(s[entry[1]:entry[1] + 2], entry[2])
        return result
        
    def query(self):
        """ this method return you a dict with the retrieved values from the heat pump """
        result = {}
        try:
            self._establishConnection()
            result["softwareVersion"] = self._getVersion()
            result.update(self._getActualValues())
        finally:
            self._closeConnection()
        return result
        

# Main program: only for testing
def main():
    aP = Protocol()
    print aP.query()


if __name__ == '__main__':
    main()

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
    This is the main module for the heatpump Monitor. It forks into the background
    and should to a polling every 60 secs. It is quit simple at this point, no
    config files or almost no error handling.
    
    Written by Robert Penz <robert@penz.name>
"""

# the configuration
serialDevice = "/dev/ttyS0"
databaseFile = "/var/lib/heatpumpMonitor/heatpumpMonitor.rrd"
renderOutputPath = "/var/www/graphs/"
renderInterval = 5

myLogFile = "/var/log/heatpumpMonitor.log"
myPidFile = "/var/run/heatpumpMonitor.pid"

########################### no changes beyond here required ##############################

#TODO: Create a common log system which is able to write a timestamp before the entry
#TODO: implement asyncron upload to webspace

import time
import sys
import traceback

import protocol
import storage
import render
import deamon


# Print usage message and exit
def usage(*args):
    sys.stdout = sys.stderr
    print __doc__
    print 50*"-"
    for msg in args: print msg
    sys.exit(2)

def logError(e):
    """ prints a string which a human readable error text """
    print "========="
    # args can be empty
    if e.args:
        if len(e.args) > 1:
            print str(e.args)
        else:
            print e.args[0]
    else:
        # print exception class name
        print str(e.__class__)
    print "---------"
    print traceback.format_exc()
    print "========="
    sys.stdout.flush()
    
    
def doMonitor():
    print "Starting ..."
    sys.stdout.flush()
    
    p = protocol.Protocol(serialDevice)
    s = storage.Storage(databaseFile)
    r = render.Render(databaseFile, renderOutputPath)
    
    print "Up and running"
    sys.stdout.flush()
    
    counter = 0
    while 1:
        startTime = time.time()
        try:
            values = p.query()
        except Exception, e:
            # log the error and just try it again in 120 sec - sometimes the heatpump returns an error and works
            # seconds later again
            logError(e)
            time.sleep(120 - (time.time() - startTime))
            continue
            
        s.add(values)
        if counter % renderInterval == 0:
            r.render()
        counter += 1
        # lets make sure it is aways 60 secs interval, no matter how long the last run took
        time.sleep(60 - (time.time() - startTime))


# Main program: parse command line and start processing
def main():
    deamon.startstop(stdout=myLogFile, pidfile=myPidFile)
    doMonitor()
    
if __name__ == '__main__':
    main()

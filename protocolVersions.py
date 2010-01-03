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
    This module handles the version specific settings of the protocol to the heat
    pump. It loads them from the ini files and provides an interface for the
    protocol.py module.
    
    Written by Robert Penz <robert@penz.name>
"""

from ConfigParser import *


class ProtocolVersions:
    _config = None
    _configFile = None
    def __init__(self, versionsConfigsDirectory = "/usr/local/heatpump/protocolVersions"):
        
        if not configFile:
            configFile = defaultConfigFile

        if not os.path.isfile(configFile):
            sys.stdout = sys.stderr
            print "Error: Cannot find config file %r" % configFile
            sys.exit(2)

        self._config = SafeConfigParser()
        self._config.read(configFile)
        self._configFile = configFile


# Main program: only for testing
def main():
    aP = Protocol()
    print aP.query()


if __name__ == '__main__':
    main()

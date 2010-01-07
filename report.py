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
    this module contains the methods for sending mail reports
"""

import smtplib
from email.MIMEText import MIMEText
import time

class Report:

    _config = None
    _useStdout = None
    _noNewReport = None

    def __init__(self, config):
        self._config = config

    def queryErrorThresholdExceeded(self):
        """ send a report that the query error threshold got exceeded """
        self._sendMail(self._config.getQueryErrorThresholdExceededSubject(), self._config.getQueryErrorThresholdExceededBody())

    def counterDecreased(self, name, reference, actual):
        """ send a report that the counter decreased """
        tmp = {"name": name, "reference": reference, "actual": actual}
        self._sendMail(self._config.getCounterDecreasedSubject() % tmp, self._config.getCounterDecreasedBody() % tmp)
        
    def counterIncreased(self, name, reference, actual):
        """ send a report that the counter increased """
        tmp = {"name": name, "reference": reference, "actual": actual}
        self._sendMail(self._config.getCounterIncreasedSubject() % tmp, self._config.getCounterIncreasedBody() % tmp)
            
    ## ###############################  internal methods  ################################################
    
    def _sendMail(self, subject, body):
        """ the actual mail build and send method """
        # Create a text/plain message
        msg = MIMEText(body, _charset = "utf-8")
        msg['Subject'] = subject
        msg['From'] = self._config.getFromAddress()
        msg['To'] = ",".join(self._config.getToAddresses())
        msg['Date'] = time.strftime('%a, %d %b %Y %H:%M:%S +0000', time.gmtime())
        
        # Send the message via our own SMTP server, but don't include the
        # envelope header.
        s = smtplib.SMTP()
        s.connect(self._config.getSmtpHost())
        s.sendmail(self._config.getFromAddress(), self._config.getToAddresses() , msg.as_string())
        s.close()

# Main program: parse command line and start processing
def main():
    import config_manager
    myReport = Report(config_manager.ConfigManager("heatpumpMonitor.ini"))
    myReport.counterIncreased(name = "testX", reference = 123, actual = 124)
    
if __name__ == '__main__':
    main()


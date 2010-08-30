
#!/usr/bin/python
# -*- coding: utf-8 -*-
""" This file is part of B{Domogik} project (U{http://www.domogik.org}). 

License 
======= 

B{Domogik} is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

B{Domogik} is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Domogik. If not, see U{http://www.gnu.org/licenses}.

Plugin purpose
==============

Get informations about plcbus

@author: Capof <capof@wanadoo.fr> 
@copyright:(C) 2007-2009 Domogik project 
@license: GPL(v3) 
@organization: Domogik 
"""
from threading import Event
import traceback
import time

from domogik.xpl.common.helper import Helper
from domogik.xpl.common.helper import HelperError 
from domogik.common import logger 
from domogik.xpl.lib.plcbus import PLCBUSException 
from domogik.xpl.lib.plcbus import PLCBUSAPI 
from domogik.xpl.lib.PLCBusSerialHandler import serialHandler


ACCESS_ERROR = "Access to PLCBUS device is not possible. Does your user have the good permissions ? " 

class plcbus(Helper):
    def __init__(self):
        self._event = Event()
        self.liste_trouve = []
        self.commands = \
            { "all" :
                {
                "cb" : self.all,
                "desc" : "Show all devices found on plcbus network",
                "min_args" : 1,
                "usage" : "find device for specified  house code <house code>"
                }
            }
        log = logger.Logger('plcbus-helper')
        self._log = log.get_logger()
        device = '/dev/plcbus'
        self.api1 = PLCBUSAPI(self._log, device, self._command_cb, self._message_cb)

    def all(self, args = None):
        self._usercode = '00'
        self.api1.send("GET_ALL_ID_PULSE", args[0] , self._usercode )
        time.sleep(1)
        self.api1.send("GET_ALL_ON_ID_PULSE", args[0] , self._usercode )
        
        self._event.wait()
        self._event.clear()
        return self.liste_trouve

    def _command_cb(self, f):
        print "command : %s" % f["d_command"]
        if f["d_command"] == "GET_ALL_ID_PULSE":
            data = int("%s%s" % (f["d_data1"], f["d_data2"]))
            house = f["d_home_unit"][0]

            for i in range(0,16):
                unit = data >> i & 1
                code = "%s%s" % (house, i+1)
                if unit == 1 :
                    self.liste_trouve.append("%s%s" % (code,"trouve"))

        if f["d_command"] == "GET_ALL_ON_ID_PULSE":
            data = int("%s%s" % (f["d_data1"], f["d_data2"]))
            house = f["d_home_unit"][0]
            #self.liste_trouve.append("%s%s" % (house,data))
            print data
            for i in range(0,16):
                unit = data >> i & 1
                code = "%s%s" % (house, i+1)
                
                #if code in self.api._probe_status and (self.api._probe_status[code] != str(unit)):
                #    self.api._probe_status[code] = str(unit)
                if unit == 1:
                    self.liste_trouve.append("%s%s" % (code,"ON"))
                else:
                    self.liste_trouve.append("%s%s" % (code,"OFF"))
            self._event.set()

    def _message_cb(self, message):
        print "Message : %s " % message

MY_CLASS = {"cb" : plcbus}


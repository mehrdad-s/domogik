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

Wake on lan client

Implements
==========

- WOLListener

@author: Fritz <fritz.smh@gmail.com>
@copyright: (C) 2007-2009 Domogik project
@license: GPL(v3)
@organization: Domogik
"""

from threading import Event

from domogik.xpl.common.xplconnector import Listener
from domogik.xpl.common.plugin import XplPlugin, XplResult
from domogik.xpl.common.xplmessage import XplMessage
from domogik.xpl.common.queryconfig import Query
from domogik.xpl.lib.wol_ping import WOL, Ping


class WolPing(XplPlugin):
    """ Implements a listener for wol messages on xPL network
    """

    def __init__(self):
        """ Create listener for wake on lan
        """
        XplPlugin.__init__(self, name = 'wol_ping')

        self._stop = Event() 
        self.add_stop_cb(self.stop)

        # Configuration : interval between each ping
        self._config = Query(self.myxpl, self.log)
        res = XplResult()
        self._config.query('wol_ping', 'ping-interval', res)
        interval = res.get_value()['ping-interval']
        if interval == "None":
            interval = 60

        # Configuration : list of computers
        self.computers = {}
        num = 1
        loop = True
        while loop == True:
            self._config = Query(self.myxpl, self.log)
            res = XplResult()
            self._config.query('wol_ping', 'cmp-%s-name' % str(num), res)
            name = res.get_value()['cmp-%s-name' % str(num)]
            self._config = Query(self.myxpl, self.log)
            res = XplResult()
            self._config.query('wol_ping', 'cmp-%s-ip' % str(num), res)
            ip = res.get_value()['cmp-%s-ip' % str(num)]
            self._config = Query(self.myxpl, self.log)
            res = XplResult()
            self._config.query('wol_ping', 'cmp-%s-mac' % str(num), res)
            mac = res.get_value()['cmp-%s-mac' % str(num)]
            self._config = Query(self.myxpl, self.log)
            res = XplResult()
            self._config.query('wol_ping', 'cmp-%s-macport' % str(num), res)
            mac_port = res.get_value()['cmp-%s-macport' % str(num)]
            if name != "None":
                self.log.info("Configuration : name=%s, ip=%s, mac=%s, mac port=%s" % (name, ip, mac, mac_port))
                self.computers[name] = {"ip" : ip, "mac" : mac, 
                                        "mac_port" : mac_port}
            else:
                loop = False
            num += 1

        ### Create WOL object
        self._wolmanager = WOL(self.log)
        # Create listeners
        Listener(self.wol_cb, self.myxpl, {'schema': 'control.basic',
                'xpltype': 'xpl-cmnd', 'type': 'wakeonlan', 'current': 'HIGH'})
        self.log.debug("Listener for wake on lan created")

        ### Create Ping object
        self._pingmanager = Ping(self.log, self.ping_cb, float(interval),
                                 self.computers, self._stop)
        self.enable_hbeat()
        self._pingmanager.ping()

    def stop(self):
        ''' Set the internal flag to stop the plugin
        '''
        self.log.debug("Set stop flag")
        self._stop.set() 

    def wol_cb(self, message):
        """ Call wake on lan lib
            @param message : xPL message detected by listener
        """
        if 'device' in message.data:
            device = message.data['device']

        try:
            mac = self.computers[device]["mac"]
            port = int(self.computers[device]["mac_port"])
        except KeyError:
            self.log.warning("Computer named '%s' is not defined" % device)
            return
        
        self.log.info("Wake on lan command received for '%s' on port '%s'" %
                       (mac, port))
        #status = self._wolmanager.wake_up(mac, port)
        status = self._wolmanager.wake_up(mac, port)

        # Send xpl-trig to say plugin receive command
        if status == True:
            mess = XplMessage()
            mess.set_type('xpl-trig')
            mess.set_schema('sensor.basic')
            mess.add_data({'device' :  device})
            mess.add_data({'type' :  'wakeonlan'})
            mess.add_data({'current' :  'HIGH'})
            self.myxpl.send(mess)


    def ping_cb(self, type, computer, status):
        # Send xpl-trig to say plugin receive command
        msg = XplMessage()
        msg.set_type(type)
        msg.set_schema('sensor.basic')
        msg.add_data({'device' :  computer})
        msg.add_data({'type' :  'ping'})
        msg.add_data({'current' :  status})
        self.myxpl.send(msg)


if __name__ == "__main__":
    inst = WolPing()


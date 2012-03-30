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

@author: Maxence Dunnewind <maxence@dunnewind.net>
@copyright: (C) 2007-2009 Domogik project
@license: GPL(v3)
@organization: Domogik
"""

import logging

class ScenarioManager:
    """ This class manages the Condition instances.
    It allows to list tests and parameters, get info about them, instantiate 
    conditions and parameters, keeps track of parameter instances, etc ...
    """

    def __init__(self):
        """ Create instance """
        FORMAT = "%(asctime)-15s %(message)s"
        logging.basicConfig(format=FORMAT)

    def list_parameters(self):
        """ List the available parameters
        @return an array of the parameters, each entry is in the form :

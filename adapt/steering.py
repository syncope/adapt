# Copyright (C) 2017  Christoph Rosemann, DESY, Notkestr. 85, D-22607 Hamburg
# email contact: christoph.rosemann@desy.de
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation in  version 2
# of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor,
# Boston, MA  02110-1301, USA.

# the entry point of the calling external binary

from . import configurationHandler
from . import processingControl

class Steering():

    def __init__(self):
        self._cfghandler = configurationHandler.ConfigurationHandler()
        self._control = processingControl.ProcessingControl()
        self._processingConfig = None

    def load(self, filename):
        self._processingConfig = self._cfghandler.loadConfig(filename)

    def write(self, filename):
        self._cfghandler.writeConfig(filename, self._processingConfig)

    def process(self):
        self._control.build(self._processingConfig)
        self._control.execute()

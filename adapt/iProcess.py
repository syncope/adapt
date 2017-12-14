# Copyright (C) 2016-17  Christoph Rosemann, DESY, Notkestr. 85, D-22607 Hamburg
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

from . import processData
from . import processParameters

'''This is the abstract base class of a user programmable process.
It defines functions that have to be present in any derived process.
These are the functions, by which the framework executes actual work.'''

class IProcess():

    def __init__(self, ptype):
        self._ptype = ptype
        self._parameters = ProcessParameters()
    
    def getProcessParameters(self):
        return self._parameters

    def getConfigGUI(self):
        pass
        
    def initialize(self, data):
        pass

    def execute(self, data):
        pass

    def finalize(self, data):
        pass

    def check(self, data):
        pass

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
from .processParameters import ProcessParameter
from PyQt4 import QtCore, QtGui, uic

'''This is the abstract base class of a user programmable process.
It defines functions that have to be present in any derived process.
These are the functions, by which the framework executes actual work.'''

class IProcess():

    def __init__(self, ptype):
        self._ptype = ptype
        self._parameters = processParameters.ProcessParameters()
        self._parametersset = False

    def getProcessParameters(self):
        return self._parameters

    def setParameterValues(self, someDict):
        '''Set the values of the parameters by a dictionary.'''
        for pname, pparam in self._parameters.items():
            try:
                pparam.set(someDict[pname])
            except KeyError:
                if pparam.isOptional:
                    continue
                else:
                    raise ValueError("Can't set process parameters, value of name " + str(pp.name) + " is missing.")

    def _internalCheck(self):
        return True

    def getConfigGUI(self):
        pass

    def initialize(self):
        pass

    def execute(self, data):
        pass

    def loopExecute(self, datalist):
        for elem in datalist:
            self.execute(elem)

    def finalize(self, data):
        pass

    def loopFinalize(self, datalist):
        for elem in datalist:
            self.finalize(elem)

    def check(self, data):
        pass

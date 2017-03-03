# Copyright (C) 2016  Christoph Rosemann, DESY, Notkestr. 85, D-22607 Hamburg
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
from . import utilities


'''This is the abstract base class of a user programmable process.
It defines functions that have to be present in any derived process.
These are the functions, by which the framework executes actual work.'''


class ProcessParameter():

    def __init__(self, name, paramtype, optional=False):
        self._name = name
        self._type = paramtype
        self._value = None
        self._optional = optional

    def getName(self):
        return self._name

    def getType(self):
        return self._type

    def isOptional(self):
        return self._optional

    def getValue(self):
        return self._value

    def setValue(self, value):
        self._value = value


class IProcessDefinition():

    def __init__(self):
        self._ptype = ""
        self._parameters = {}

    def getProcessType(self):
        return self._ptype

    def createParameter(self, name, paramtype, value=None, optional=False):
        self._parameters[name] = ProcessParameter(name, paramtype, optional=optional)
        if(value != None):
            self.setParameterValue(name, value)

    def setParameterValue(self, paramname, value):
        p = self._parameters[paramname]
        p.setValue(utilities.castValueToType(value, p.getType()))

    def getParameterValue(self, paramname):
        return self._paramaters[paramname].getValue()

    def getParameter(self, name):
        return self._parameters[name]

    def getParameters(self):
        return self._parameters


class IProcess():

    def __init__(self, processDefinition):
        self._input = []
        self._output = []
        #~ self._procParams = processParameters
        self._parameters = {}
        for param in processDefinition.getParameters().values():
            self._parameters[param.getName()] = param.getValue()

    def parameter(self, name):
        return self._parameters[name]

    def parameterValue(self, name):
        return self._parameters[name].getValue()

    def initialize(self, data):
        pass

    def execute(self, data):
        pass

    def finalize(self, data):
        pass

    def check(self, data):
        pass

if __name__ == "__main__":
    print("[IProcess] This is not meant to be instantiated.")

    i = IProcessDefinition()
    print("i have a " + repr(i))
    print(" its parameters are: " + repr(i.getParameters()))

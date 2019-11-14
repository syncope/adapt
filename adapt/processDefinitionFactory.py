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

# the factory that can create process definitions

from . import processes


class ProcessDefinitionFactory():

    def __init__(self):
        pass

    def createProcessDefinitionFromDict(self, simpleDict):
        try:
            # pdt: process defition type
            pdt = simpleDict["type"]
            procDefName = pdt + "def"
        except KeyError:
            raise Exception("The process definition type is unknown."
                            + " Check spelling or its existence")

        tempProcDef = getattr(getattr(processes, pdt), procDefName)()

        for param in tempProcDef.getParameters():
            try:
                tempProcDef.setParameterValue(param, simpleDict[param])
            except KeyError:
                if(tempProcDef.getParameters()[param].isOptional()):
                    pass
                else:
                    raise KeyError("Missing value for mandatory "
                                   + " parameter " + param
                                   + " in definition for " + pdt)
        return tempProcDef

    def createProcessDefinitionFromProcess(self, proc):
        pass


if __name__ == "__main__":
    k = ProcessDefinitionFactory()
    d = {"type": "globaldata"}
    k.createProcessDefinitionFromDict(d)

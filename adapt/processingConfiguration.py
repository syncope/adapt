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

# a simple abstract definition for the core processing model:
#  - an execution ordered list holding names
#  - a map of processes, defined by name, type its associated values


class ProcessingConfiguration():

    def __init__(self, execList=[], pDefDict={}):
        self._executionOrder = execList
        self._definitionDict = pDefDict

    def addProcessDefinition(self, pDefDict):
        self._definitionDict = pDefDict

    def addSingleProcessDefinition(self, name, process):
        self._definitionDict[name] = process

    def removeProcess(self, name):
        self._definitionDict.pop(name)
        self._executionOder.remove(name)

    def getProcessDefinitions(self):
        return self._definitionDict

    def setOrderOfExecution(self, execList):
        self._executionOrder = execList

    def getOrderOfExecution(self):
        return self._executionOrder

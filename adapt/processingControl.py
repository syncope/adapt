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

# potentially the central control class
# it instantiates processes, keeps the master list of execution
# and owns the central instance of the data object (!)
# maybe presumably it needs a better name


from . import iProcess
from . import processData
from . import processBuilder

class ProcessingControl():

    def __init__(self):
        self._pBuilder = processBuilder.ProcessBuilder()
        self._data = processData.ProcessData()
        self._masterExecutionlist = []

    def getProcessTypeList(self):
        return self._pBuilder.getProcessTypeList()

    def resetList(self):
        self._masterExecutionlist = []

    def build(self, processConfig):
        # this is a potentially raw object
        # dismantle and check before instantiating anything!
 
        execOrder = processConfig.getOrderOfExecution()
        pDefs = processConfig.getProcessDefinitions()

        for pname in execOrder:
            self._masterExecutionlist.append( self._pBuilder.createProcessFromDictionary(pDefs[pname]) )

    def execute(self):
        self._runInitialization()
        self._runLoop()
        self._runFinalization()

    def _runInitialization(self):
        for proc in self._masterExecutionlist:
            proc.initialize(self._data)

    def _runLoop(self):
        try:
            while(1):
                for proc in self._masterExecutionlist:
                    proc.execute(self._data)
                self._data.clearCurrent()
        except StopIteration:
            return

    def _runFinalization(self):
        for proc in self._masterExecutionlist:
            proc.finalize(self._data)

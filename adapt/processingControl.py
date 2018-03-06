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
# presumably it needs a better name


from . import iProcess
from . import processData
from . import processBuilder

class ProcessingControl():
    '''The central control object for batch processing.
       It holds the elements to build processes from their description,
       the list of processes to be run and the central data exchange object.'''

    def __init__(self):
        self._procBuilder = processBuilder.ProcessBuilder()
        self._data = processData.ProcessData()
        self._batchExecutionlist = []

    def getProcessTypeList(self):
        return self._procBuilder.getProcessTypeList()

    def resetList(self):
        self._batchExecutionlist = []

    def build(self, processConfig):
        # this is a potentially raw object
        # TODO: dismantle and check before instantiating anything!
 
        execOrder = processConfig.getOrderOfExecution()
        pDefs = processConfig.getProcessDefinitions()

        for pname in execOrder:
            self._batchExecutionlist.append( self._procBuilder.createProcessFromDictionary(pDefs[pname]) )

    def execute(self):
        self._runInitialization()
        self._runLoop()
        self._runFinalization()

    def _runInitialization(self):
        for proc in self._batchExecutionlist:
            proc.initialize(self._data)

    def _runLoop(self):
        try:
            while(1):
                for proc in self._batchExecutionlist:
                    proc.execute(self._data)
                self._data.clearCurrent()
        except StopIteration:
            return

    def _runFinalization(self):
        for proc in self._batchExecutionlist:
            proc.finalize(self._data)

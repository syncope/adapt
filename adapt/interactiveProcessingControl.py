# Copyright (C) 2018 Christoph Rosemann, DESY, Notkestr. 85, D-22607 Hamburg
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

# the central control class for interactive processing
# it holds an instance of the batch processing master

from . import processingControl
from . import processData
from . import processBuilder


class InteractiveProcessingControl():
    '''The central control object for interactive processing.
       It holds the elements to build processes from their description,
       the list of processes to be run and the central data exchange object.'''

    def __init__(self):
        self._procControl = processingControl.ProcessingControl()
        self._dataList = []
        self._processList = []
        
    def getProcessTypeList(self):
        return self._procControl.getProcessTypeList()

    def getDataList(self):
        return self._dataList

#~ 
    #~ def build(self, processConfig):
        #~ # this is a potentially raw object
        #~ # TODO: dismantle and check before instantiating anything!
 #~ 
        #~ execOrder = processConfig.getOrderOfExecution()
        #~ pDefs = processConfig.getProcessDefinitions()
#~ 
        #~ for pname in execOrder:
            #~ self._batchExecutionlist.append( self._procBuilder.createProcessFromDictionary(pDefs[pname]) )
#~ 
    #~ def execute(self):
        #~ self._runInitialization()
        #~ self._runLoop()
        #~ self._runFinalization()
#~ 
    #~ def _runInitialization(self):
        #~ for proc in self._batchExecutionlist:
            #~ proc.initialize(self._data)
#~ 
    #~ def _runLoop(self):
        #~ try:
            #~ while(1):
                #~ for proc in self._batchExecutionlist:
                    #~ proc.execute(self._data)
                #~ self._data.clearCurrent()
        #~ except StopIteration:
            #~ return
#~ 
    #~ def _runFinalization(self):
        #~ for proc in self._batchExecutionlist:
            #~ proc.finalize(self._data)

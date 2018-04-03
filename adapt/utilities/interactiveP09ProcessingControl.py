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

from adapt import processingControl
from adapt import processData
from adapt import processBuilder

from adapt.processes import specfilereader
from adapt.processes import iintdefinition
from adapt.processes import filter1d
from adapt.processes import subsequenceselection
from adapt.processes import curvefitting
from adapt.processes import gendatafromfunction
from adapt.processes import backgroundsubtraction
from adapt.processes import trapezoidintegration
from adapt.processes import iintfinalization


class InteractiveP09ProcessingControl():
    '''The central control object for interactive processing.
       It holds the elements to build processes from their description,
       the list of processes to be run and the central data exchange object.'''

    def __init__(self):
        self._procControl = processingControl.ProcessingControl()
        self._procBuilder = processBuilder.ProcessBuilder()
        self._dataList = []
        self._processList = []
        self._motorName = ""
        self._rawName = "rawdata"
        self._observableName = "observable"
        self._despObservableName = "despikedobservable"
        self._backgroundPointsName = "bkgPoints"
        self._signalName = "signalObservable"
        self._processNames = [ "read", 
                               "observabledef",
                               "despike",
                               "bkgselect",
                               "bkgfit",
                               "calcbkgpoints",
                               "bkgsubtract",
                               "signalcurvefit",
                               "trapint",
                               "finalize" ]
        self._procRunList = []
        self._processParameters = {}
        self._setupProcessParameters()
        self._setupDefaultNames()

    def _setupProcessParameters(self):
        self._processParameters["read"] = specfilereader.specfilereader().getProcessDictionary()
        self._processParameters["observabledef"] = iintdefinition.iintdefinition().getProcessDictionary()
        self._processParameters["despike"] = filter1d.filter1d().getProcessDictionary()
        self._processParameters["bkgselect"] = subsequenceselection.subsequenceselection().getProcessParameters()
        self._processParameters["bkgfit"] = curvefitting.curvefitting().getProcessParameters()
        self._processParameters["calcbkgpoints"] = gendatafromfunction.gendatafromfunction().getProcessParameters()
        self._processParameters["bkgsubtract"] =backgroundsubtraction.backgroundsubtraction().getProcessParameters()
        self._processParameters["signalcurvefit"] =  curvefitting.curvefitting().getProcessParameters()
        self._processParameters["trapint"] = trapezoidintegration.trapezoidintegration().getProcessParameters()
        self._processParameters["finalize"] = iintfinalization.iintfinalization().getProcessParameters()

    def _setupDefaultNames(self):
        self._processParameters["read"]["outputdata"] = self._rawName
        # from out to in:
        self._processParameters["observabledef"]["input"] = self._rawName
        self._processParameters["observabledef"]["observableoutput"] =  self._observableName
        # from out to in:
        self._processParameters["despike"]["input"] =  self._observableName
        self._processParameters["despike"]["method"] = "p09despiking"
        self._processParameters["despike"]["output"] =  self._despObservableName
        # from out to in
        self._processParameters["bkgselect"].setValue("input",[ self._despObservableName, self._motorName])
        self._processParameters["bkgselect"].setValue("output", ["bkgX" ,"bkgY"])
        self._processParameters["bkgselect"].setValue("selectors", ["selectfromstart" ,"selectfromend"])
        self._processParameters["bkgselect"].setValue("startpointnumber", 3)
        self._processParameters["bkgselect"].setValue("endpointnumber", 3)
        # fit bkg
        self._processParameters["bkgfit"].setValue("xdata","bkgX")
        self._processParameters["bkgfit"].setValue("ydata","bkgY")
        self._processParameters["bkgfit"].setValue("error","None")
        self._processParameters["bkgfit"].setValue("result","bkgfitresult")
        self._processParameters["bkgfit"].setValue("model",{ "linearModel" : {"name" : "lin_"}})
        # calc bkg points
        self._processParameters["calcbkgpoints"].setValue("fitresult","bkgfitresult")
        self._processParameters["calcbkgpoints"].setValue("xdata",self._motorName)
        self._processParameters["calcbkgpoints"].setValue("output", self._backgroundPointsName)
        # subtract bkg
        self._processParameters["bkgsubtract"].setValue("input", self._despObservableName)
        self._processParameters["bkgsubtract"].setValue("output", self._signalName)
        self._processParameters["bkgsubtract"].setValue("background", self._backgroundPointsName)
        
    def useNoDespiking(self):
        self._processParameters["bkgselect"].setValue("input", self._observableName)
        self._processParameters["bkgselect"].setValue("input", [self._observableName, self._motorName] )
        self._processParameters["bkgsubtract"].setValue("input", self._observableName)
        
    def getRawDataName(self):
        return self._rawName

    def getMotorName(self):
        return self._motorName

    def setMotorName(self, motor):
        self._motorName= motor
        self._processParameters["bkgselect"].setValue("input",[ self._despObservableName, self._motorName])
        self._processParameters["calcbkgpoints"].setValue("xdata", self._motorName)

    def getObservableName(self):
        return self._observableName

    def getDespikedObservableName(self):
        return self._despObservableName

    def getBackgroundName(self):
        return self._backgroundPointsName

    def getSignalName(self):
        return self._signalName

    def getProcessTypeList(self):
        return self._procControl.getProcessTypeList()

    def createDataList(self, data, name):
        for datum in data:
            pd = processData.ProcessData()
            pd.addData(name, datum)
            self._dataList.append(pd)

    def getDataList(self):
        return self._dataList

    def createAndInitialize(self, pdict):
        proc = self._procBuilder.createProcessFromDictionary(pdict)
        proc.initialize()
        return proc

    def createAndBulkExecute(self, pDict):
        if pDict is None:
            return
        proc = self._procBuilder.createProcessFromDictionary(pDict)
        proc.initialize()
        proc.loopExecute(self._dataList)

    def loadConfig(self, processConfig):
        print("ctrl: loading config")
        self._procRunList.clear()
        execOrder = processConfig.getOrderOfExecution()
        pDefs = processConfig.getProcessDefinitions()
        for proc in execOrder:
            if proc in self._processNames:
                print("processs: " + str(proc) + " is in the list!" )
                self._procRunList.append(proc)
                for k, v in pDefs[proc].items():
                    print(" accessing: key/value: " + str(k) + " // " + str(v))
                    if k != "type":
                        self._processParameters[proc][k] =v
            else:
                print("Wrong configuration file, unrecognized process name/type: " + str(proc))        

    def getSFRDict(self):
        return self._processParameters["read"]

    def getOBSDict(self):
        return self._processParameters["observabledef"]

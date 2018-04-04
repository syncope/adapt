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
        self._despObservableName = "despikedObservable"
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
        self._processParameters["bkgselect"] = subsequenceselection.subsequenceselection().getProcessDictionary()
        self._processParameters["bkgfit"] = curvefitting.curvefitting().getProcessDictionary()
        self._processParameters["calcbkgpoints"] = gendatafromfunction.gendatafromfunction().getProcessDictionary()
        self._processParameters["bkgsubtract"] =backgroundsubtraction.backgroundsubtraction().getProcessDictionary()
        self._processParameters["signalcurvefit"] =  curvefitting.curvefitting().getProcessDictionary()
        self._processParameters["trapint"] = trapezoidintegration.trapezoidintegration().getProcessDictionary()
        self._processParameters["finalize"] = iintfinalization.iintfinalization().getProcessDictionary()

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
        self._processParameters["bkgselect"]["input"] = [ self._despObservableName, self._motorName]
        self._processParameters["bkgselect"]["output"] =  ["bkgX" ,"bkgY"]
        self._processParameters["bkgselect"]["selectors"] =  ["selectfromstart" ,"selectfromend"]
        self._processParameters["bkgselect"]["startpointnumber"] =  3
        self._processParameters["bkgselect"]["endpointnumber"] =  3
        # fit bkg
        self._processParameters["bkgfit"]["xdata"] = "bkgX"
        self._processParameters["bkgfit"]["ydata"] = "bkgY"
        self._processParameters["bkgfit"]["error"] = "None"
        self._processParameters["bkgfit"]["result"] = "bkgfitresult"
        self._processParameters["bkgfit"]["model"] = { "linearModel" : {"name" : "lin_"}}
        # calc bkg points
        self._processParameters["calcbkgpoints"]["fitresult"] = "bkgfitresult"
        self._processParameters["calcbkgpoints"]["xdata"] = self._motorName
        self._processParameters["calcbkgpoints"]["output"] =  self._backgroundPointsName
        # subtract bkg
        self._processParameters["bkgsubtract"]["input"] =  self._despObservableName
        self._processParameters["bkgsubtract"]["output"] =  self._signalName
        self._processParameters["bkgsubtract"]["background"] =  self._backgroundPointsName
        
    def useNoDespiking(self):
        self._processParameters["bkgselect"]["input"] =  self._observableName
        self._processParameters["bkgselect"]["input"] =  [self._observableName, self._motorName] 
        self._processParameters["bkgsubtract"]["input"] =  self._observableName
        
    def getRawDataName(self):
        return self._rawName

    def getMotorName(self):
        return self._motorName

    def setMotorName(self, motor):
        self._motorName= motor
        self._processParameters["bkgselect"]["input"] = [ self._despObservableName, self._motorName]
        self._processParameters["calcbkgpoints"]["xdata"] =  self._motorName

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
        print("creating and running from dict: " + str(pDict))

        if pDict is None:
            return
        proc = self._procBuilder.createProcessFromDictionary(pDict)
        proc.initialize()
        proc.loopExecute(self._dataList)

    def loadConfig(self, processConfig):
        self._procRunList.clear()
        execOrder = processConfig.getOrderOfExecution()
        pDefs = processConfig.getProcessDefinitions()
        for proc in execOrder:
            if proc in self._processNames:
                self._procRunList.append(proc)
                for k, v in pDefs[proc].items():
                    #~ if k != "type":
                        #~ self._processParameters[proc][k] =v
                    self._processParameters[proc][k] =v
            else:
                print("Wrong configuration file, unrecognized process name/type: " + str(proc))        

    def getSFRDict(self):
        return self._processParameters["read"]

    def getOBSDict(self):
        return self._processParameters["observabledef"]

    def getDESDict(self):
        try:
            return self._processParameters["despike"]
        except KeyError:
            return {}

    def getBKGDicts(self):
        print("getting the DICTS: sel is: " + str(self._processParameters["bkgselect"]))
        print("getting the DICTS: fit is: " + str(self._processParameters["bkgfit"]))
        try:
            return (self._processParameters["bkgselect"],
                    self._processParameters["bkgfit"],
                    self._processParameters["calcbkgpoints"],
                    self._processParameters["bkgsubtract"] )            
        except KeyError:
            return ({}, {}, {}, {})

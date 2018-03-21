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
                               "curvefit",
                               "trapint",
                               "finalize" ]
        self._processHelper = {}
        self._setupProcessHelper()
        self._setupDefaultNames()

    def _setupProcessHelper(self):
        self._processHelper["read"] = iintGUIhelper("read", specfilereader.specfilereader().getProcessParameters().keys())
        self._processHelper["observabledef"] = iintGUIhelper("observabledef", iintdefinition.iintdefinition().getProcessParameters().keys())
        self._processHelper["despike"] = iintGUIhelper("despike", filter1d.filter1d().getProcessParameters().keys())
        self._processHelper["bkgselect"] = iintGUIhelper("bkgselect", subsequenceselection.subsequenceselection().getProcessParameters().keys())
        self._processHelper["bkgfit"] = iintGUIhelper("bkgfit", curvefitting.curvefitting().getProcessParameters().keys())
        self._processHelper["calcbkgpoints"] = iintGUIhelper("calcbkgpoints", gendatafromfunction.gendatafromfunction().getProcessParameters().keys())
        self._processHelper["bkgsubtract"] = iintGUIhelper("bkgsubtract", backgroundsubtraction.backgroundsubtraction().getProcessParameters().keys()) 
        self._processHelper["curvefit"] = iintGUIhelper("curvefit", curvefitting.curvefitting().getProcessParameters().keys())
        self._processHelper["trapint"] = iintGUIhelper("trapint", trapezoidintegration.trapezoidintegration().getProcessParameters().keys()) 
        self._processHelper["finalize"] = iintGUIhelper("finalize", iintfinalization.iintfinalization().getProcessParameters().keys()) 

    def _setupDefaultNames(self):
        self._processHelper["read"].setParamValue("outputdata","rawdata")
        # from out to in:
        self._processHelper["observabledef"].setParamValue("input","rawdata")
        self._processHelper["observabledef"].setParamValue("observableoutput", self._observableName)
        # from out to in:
        self._processHelper["despike"].setParamValue("input", self._observableName)
        self._processHelper["despike"].setParamValue("method","p09despiking")
        self._processHelper["despike"].setParamValue("output", self._despObservableName)
        # from out to in
        self._processHelper["bkgselect"].setParamValue("input",[ self._despObservableName, self._motorName])
        self._processHelper["bkgselect"].setParamValue("output", ["bkgX" ,"bkgY"])
        self._processHelper["bkgselect"].setParamValue("selectors", ["selectfromstart" ,"selectfromend"])
        self._processHelper["bkgselect"].setParamValue("startpointnumber", 3)
        self._processHelper["bkgselect"].setParamValue("endpointnumber", 3)
        # fit bkg
        self._processHelper["bkgfit"].setParamValue("xdata","bkgX")
        self._processHelper["bkgfit"].setParamValue("ydata","bkgY")
        self._processHelper["bkgfit"].setParamValue("error","None")
        self._processHelper["bkgfit"].setParamValue("result","bkgfitresult")
        self._processHelper["bkgfit"].setParamValue("model",{ "linearModel" : {"name" : "lin_"}})
        # calc bkg points
        self._processHelper["calcbkgpoints"].setParamValue("fitresult","bkgfitresult")
        self._processHelper["calcbkgpoints"].setParamValue("xdata",self._motorName)
        self._processHelper["calcbkgpoints"].setParamValue("output", self._backgroundPointsName)
        # subtract bkg
        self._processHelper["bkgsubtract"].setParamValue("input", self._despObservableName)
        self._processHelper["bkgsubtract"].setParamValue("output", self._signalName)
        self._processHelper["bkgsubtract"].setParamValue("background", self._backgroundPointsName)
        
    def useNoDespiking(self):
        self._processHelper["bkgselect"].setParamValue("input", self._observableName)
        self._processHelper["bkgselect"].setParamValue("input", [self._observableName, self._motorName] )
        self._processHelper["bkgsubtract"].setParamValue("input", self._observableName)
        
    def getMotorName(self):
        return self._motorName

    def setMotorName(self, motor):
        self._motorName= motor
        self._processHelper["bkgselect"].setParamValue("input",[ self._despObservableName, self._motorName])
        self._processHelper["calcbkgpoints"].setParamValue("xdata", self._motorName)

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

    def convertToDataList(self, data, name):
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

    def loadConfigDict(self, someDict):
        for k,v in someDict.items():
            print(" key: " + str(k) + " has value: " + str(v))

class iintGUIhelper():

    def __init__(self, name=None, paramnames=None):
        self._name = name
        self._paramDict = {p: None for p in paramnames}

    def setParamValue(self, name, value):
        try:
            self._paramDict[name] = value
        except KeyError:
            raise KeyError("[helper] setting the value of param " + str(name) + " failed, name is unknown")

    def getParamDict(self):
        return self._paramDict

    def getName(self):
        return self._name

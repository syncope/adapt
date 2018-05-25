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
from adapt import processingConfiguration

from adapt.processes import specfilereader
from adapt.processes import iintdefinition
from adapt.processes import filter1d
from adapt.processes import subsequenceselection
from adapt.processes import curvefitting
from adapt.processes import gendatafromfunction
from adapt.processes import backgroundsubtraction
from adapt.processes import trapezoidintegration
from adapt.processes import iintfinalization

import numpy as np

class InteractiveP09ProcessingControl():
    '''The central control object for interactive processing.
       It holds the elements to build processes from their description,
       the list of processes to be run and the central data exchange object.'''

    def __init__(self):
        self._procControl = processingControl.ProcessingControl()
        self._procBuilder = processBuilder.ProcessBuilder()
        self._dataList = []
        self._processList = []
        self._nodespike = True
        self._nobkg = True
        self._notrapint = True
        self._motorName = ""
        self._rawName = "rawdata"
        self._observableName = "observable"
        self._despObservableName = "despikedObservable"
        self._backgroundPointsName = "bkgPoints"
        self._signalName = "signalObservable"
        self._fittedSignalName = "signalcurvefitresult"
        self._fitSignalPointsName = "signalFitPoints"
        self._trapintName = "trapezoidIntegral"
        self._processNames = [ "read", 
                               "observabledef",
                               "despike",
                               "bkgselect",
                               "bkgfit",
                               "calcbkgpoints",
                               "bkgsubtract",
                               "signalcurvefit",
                               "calcfitpoints",
                               "trapint",
                               "finalize" ]
        self._procRunList = []
        self._processParameters = {}
        self._setupProcessParameters()
        self._setupDefaultNames()

    def resetAll(self):
        self._setupProcessParameters()
        self._setupDefaultNames()
        for elem in self._dataList:
            elem.clearAll()
        del self._dataList[:]
        self._dataList = []
        del self._processList[:]
        self._processList = []
        self._nodespike = True
        self._nobkg = True
        self._notrapint = True
        self._motorName = ""
        self._rawName = "rawdata"
        self._observableName = "observable"
        self._despObservableName = "despikedObservable"
        self._backgroundPointsName = "bkgPoints"
        self._signalName = "signalObservable"
        self._fittedSignalName = "signalcurvefitresult"
        self._fitSignalPointsName = "signalFitPoints"
        self._trapintName = "trapezoidIntegral"

    def _setupProcessParameters(self):
        self._processParameters["read"] = specfilereader.specfilereader().getProcessDictionary()
        self._processParameters["observabledef"] = iintdefinition.iintdefinition().getProcessDictionary()
        self._processParameters["despike"] = filter1d.filter1d().getProcessDictionary()
        self._processParameters["bkgselect"] = subsequenceselection.subsequenceselection().getProcessDictionary()
        self._processParameters["bkgfit"] = curvefitting.curvefitting().getProcessDictionary()
        self._processParameters["calcbkgpoints"] = gendatafromfunction.gendatafromfunction().getProcessDictionary()
        self._processParameters["bkgsubtract"] =backgroundsubtraction.backgroundsubtraction().getProcessDictionary()
        self._processParameters["signalcurvefit"] =  curvefitting.curvefitting().getProcessDictionary()
        self._processParameters["calcfitpoints"] = gendatafromfunction.gendatafromfunction().getProcessDictionary()
        self._processParameters["trapint"] = trapezoidintegration.trapezoidintegration().getProcessDictionary()
        self._processParameters["finalize"] = iintfinalization.iintfinalization().getProcessDictionary()
        self._fitmodels = curvefitting.curvefitting().getFitModels()

    def _setupDefaultNames(self):
        self._processParameters["read"]["output"] = self._rawName
        # from out to in:
        self._processParameters["observabledef"]["input"] = self._rawName
        self._processParameters["observabledef"]["output"] =  self._observableName
        self._processParameters["observabledef"]["detector_column"] =  "exp_c01"
        self._processParameters["observabledef"]["monitor_column"] = "sumvfcs_counts"
        self._processParameters["observabledef"]["exposureTime_column"] = "exp_t01"
        
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
        self._processParameters["bkgfit"]["usepreviousresult"] = 0
        self._processParameters["bkgfit"]["model"] = { "lin_" : {"modeltype" : "linearModel"}}
        # calc bkg points
        self._processParameters["calcbkgpoints"]["fitresult"] = "bkgfitresult"
        self._processParameters["calcbkgpoints"]["xdata"] = self._motorName
        self._processParameters["calcbkgpoints"]["output"] =  self._backgroundPointsName
        # subtract bkg
        self._processParameters["bkgsubtract"]["input"] =  self._despObservableName
        self._processParameters["bkgsubtract"]["output"] =  self._signalName
        self._processParameters["bkgsubtract"]["background"] =  self._backgroundPointsName
        # signal fitting
        self._processParameters["signalcurvefit"]["xdata"] = self._motorName
        self._processParameters["signalcurvefit"]["ydata"] = self._signalName
        self._processParameters["signalcurvefit"]["error"] = "None"
        self._processParameters["signalcurvefit"]["usepreviousresult"] = 1
        self._processParameters["signalcurvefit"]["result"] = self._fittedSignalName
        self._processParameters["signalcurvefit"]["model"] = { "m0_" : { "modeltype": "gaussianModel"}}
        # calc fitted signal points
        self._processParameters["calcfitpoints"]["fitresult"] = self._fittedSignalName
        self._processParameters["calcfitpoints"]["xdata"] = self._motorName
        self._processParameters["calcfitpoints"]["output"] =  self._fitSignalPointsName
        # trapezoidal integration
        self._processParameters["trapint"]["motor"] = self._motorName
        self._processParameters["trapint"]["observable"] = self._signalName
        self._processParameters["trapint"]["output"] = self._trapintName

    def getRawDataName(self):
        return self._rawName

    def getMotorName(self):
        return self._motorName

    def setMotorName(self, motor):
        self._motorName= motor
        self._processParameters["bkgselect"]["input"] = [ self._despObservableName, self._motorName]
        self._processParameters["calcbkgpoints"]["xdata"] =  self._motorName
        self._processParameters["signalcurvefit"]["xdata"] = self._motorName
        self._processParameters["calcfitpoints"]["xdata"] = self._motorName
        self._processParameters["trapint"]["motor"] = self._motorName

    def noDespiking(self):
        self._nodespike = True
        self._despObservableName = self._observableName
        self._processParameters["bkgselect"]["input"] = [ self._despObservableName, self._motorName]
        self._processParameters["bkgsubtract"]["input"] =  self._despObservableName

    def noBackground(self):
        self._nobkg = True
        self._signalName = self._despObservableName
        self._processParameters["signalcurvefit"]["ydata"] = self._signalName
        self._processParameters["trapint"]["observable"] = self._signalName

    def getObservableName(self):
        return self._observableName

    def getDespikedObservableName(self):
        return self._despObservableName

    def getBackgroundName(self):
        return self._backgroundPointsName

    def getSignalName(self):
        return self._signalName

    def getFittedSignalName(self):
        return self._fitSignalPointsName

    def getTrapezoidIntegralName(self):
        return self._trapintName

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
        proc.loopExecuteWithOverwrite(self._dataList, emitProgress=True)

    def loadConfig(self, processConfig):
        self._procRunList.clear()
        execOrder = processConfig.getOrderOfExecution()
        pDefs = processConfig.getProcessDefinitions()
        for proc in execOrder:
            if proc in self._processNames:
                self._procRunList.append(proc)
                for k, v in pDefs[proc].items():
                    self._processParameters[proc][k] =v
            else:
                print("Wrong configuration file, unrecognized process name/type: " + str(proc))
        if "trapint" in execOrder:
            self._notrapint = False
        if "despike" in execOrder:
            self._nodespike = False
        if "bkgsubtract" in execOrder:
            self._nobkg = False

    def saveConfig(self, filename):
        execlist =  [ "read", "observabledef"]
        processDict = {}
        processDict["read"] = self.getSFRDict()
        processDict["observabledef"] = self.getOBSDict()
        if processDict["observabledef"]["attenuationFactor_column"] == None:
            del processDict["observabledef"]["attenuationFactor_column"]
        if not self._nodespike:
            execlist.append("despike")
            processDict["despike"] = self.getDESDict()
        if not self._nobkg:
            execlist.append("bkgselect")
            execlist.append("bkgfit")
            execlist.append("calcbkgpoints")
            execlist.append("bkgsubtract")
            ds = self.getBKGDicts()
            processDict["bkgselect"] = ds[0]
            processDict["bkgfit"] = ds[1]
            processDict["calcbkgpoints"] = ds[2]
            processDict["bkgsubtract"] = ds[3]
        if not self._notrapint:
            execlist.append("trapint")
            processDict["trapint"] = self.getTrapIntDict()
        execlist.append("signalcurvefit")
        processDict["signalcurvefit"] = self.getSIGDict()

        procconfig = processingConfiguration.ProcessingConfiguration()
        procconfig.addProcessDefinition(processDict)
        procconfig.setOrderOfExecution(execlist)
        from adapt import configurationHandler
        handler = configurationHandler.ConfigurationHandler()
        handler.writeConfig(filename, procconfig)


    def proposeConfigfileName(self):
        suffix = ".iint"
        # use the scanlist entries and the input spec file name
        try:
            import os.path
            # TODO: fix the removal of path!
            basename = os.path.basename(self._processParameters["read"]["filename"]).split('.')[0]
        except:
            return
        # decompose the scanlist parameters
        scanlist = str(self._processParameters["read"]["scanlist"])
        stride = None
        retlist = []
        if scanlist.find(':') != -1:
            stride = int(scanlist.split(':')[-1])
            scanlist = scanlist.split(':')[0]
        scanlist = scanlist.split('[')[-1]
        scanlist = scanlist.split(']')[0]
        try:
            li = scanlist.split(',')
        except AttributeError:
            pass
        for elem in li:
            try:
                retlist.append(int(elem))
            except ValueError:
                try:
                    tmp = elem.split('-')
                    for i in tmp:
                        retlist.append(i)
                except:
                    pass
        retlist.sort()
        startnumber = retlist[0]
        endnumber = retlist[-1]
        if stride != None:
            stridesuffix = "-s" + str(stride)
        else:
            stridesuffix = ''
        return basename + "_S" + str(startnumber) + "E" + str(endnumber) + stridesuffix + suffix

    def getSFRDict(self):
        return self._processParameters["read"]

    def getOBSDict(self):
        return self._processParameters["observabledef"]

    def getDESDict(self):
        if self._nodespike:
            return {}
        try:
            return self._processParameters["despike"]
        except KeyError:
            return {}

    def getTrapIntDict(self):
        if self._notrapint:
            return {}
        try:
            return self._processParameters["trapint"]
        except KeyError:
            return {}

    def getBKGDicts(self):
        try:
            return (self._processParameters["bkgselect"],
                    self._processParameters["bkgfit"],
                    self._processParameters["calcbkgpoints"],
                    self._processParameters["bkgsubtract"] )            
        except KeyError:
            return ({}, {}, {}, {})

    def getSIGDict(self):
        try:
            return self._processParameters["signalcurvefit"]
        except KeyError:
            return {}

    def getFitModels(self):
        return curvefitting.curvefitting().getFitModels()

    def getFitModel(self, modelname, data, index):
        # needs different approach // or extension: keep the widgets
        self._signalfitter = self._fitmodels[modelname]()
        return self._signalfitter.getWidget(data[0], data[1], index=index)

    def getSignalFitDict(self):
        return self._processParameters["calcfitpoints"]

    def getTrapIntDict(self):
        if(self._notrapint):
            return {}
        else:
            return self._processParameters["trapint"]

    def useBKG(self, value):
        self._nobkg = not value
        self.noBackground()

    def useTrapInt(self, value):
        self._notrapint = not value

    def useDespike(self, value):
        self._nodespike = not value
        self.noDespiking()

    def getTrackInformation(self, name):
        value, error = [], []
        infoholder = {}
        for datum in self._dataList:
            fitresult = datum.getData(self._fittedSignalName)
            params = fitresult.params
            for param in params:
                try:
                    infoholder[params[param].name].append((params[param].value, params[param].stderr))
                except KeyError:
                    infoholder[params[param].name] =[]
                    infoholder[params[param].name].append((params[param].value, params[param].stderr))
            try:
                array = datum.getData(self._rawName).getArray(name)
                value.append(np.mean(array))
                error.append(np.std(array))
            except KeyError:
                try:
                    value.append(datum.getData(self._rawName).getCustomVar(name))
                    error.append(0.)
                except:
                    print("Can't retrieve the information of " + str(name))
                    return
        return trackedInformation(name, value, error, infoholder)

    def getSignalFitResults(self):
        resultlist = []
        try:
            for datum in self._dataList:
                scannumber = datum.getData(self.getRawDataName()).getScanNumber()
                resultlist.append(80 *"*" + '\n' + "Scan number : " + str(scannumber) + '\n') 
                resultlist.append(datum.getData(self._fittedSignalName).fit_report())
        except:
            pass
        return resultlist

    def getDefaultSignalFitResults(self):
        value, error = [], []
        infoholder = {}
        name = 'ScanNumber'
        for datum in self._dataList:
            fitresult = datum.getData(self._fittedSignalName)
            params = fitresult.params
            for param in params:
                try:
                    infoholder[params[param].name].append((params[param].value, params[param].stderr))
                except KeyError:
                    infoholder[params[param].name] =[]
                    infoholder[params[param].name].append((params[param].value, params[param].stderr))

            value.append(datum.getData(self._rawName).getScanNumber())
            error.append(0.)

        return trackedInformation(name, value, error, infoholder)

class trackedInformation():
    
    def __init__(self, name, value, error, info):
        self.name = name
        self.value = value
        self.error = error
        self.names = sorted(info.keys())
        self.values = info

    def getValues(self, name):
        tmpval = []
        for val in self.values[name]:
            tmpval.append(val[0])
        return np.array(tmpval)

    def getErrors(self, name):
        tmpval = []
        for val in self.values[name]:
            tmpval.append(val[1])
        return np.array(tmpval)


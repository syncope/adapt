# Copyright (C) 2017  Christoph Rosemann, DESY, Notkestr. 85, D-22607 Hamburg
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


from adapt.iProcess import *

import numpy as np

try:
    from pensant.models import FitModels
    from pensant.models import CompositeModel
except ImportError:
    print("[proc::curvefitting] library pensant not found; no curvefitting will be available!")
    pass


class curvefitting(IProcess):

    def __init__(self, ptype="curvefitting"):
        super(curvefitting, self).__init__(ptype)
        self._xdataPar = ProcessParameter("xdata", str)
        self._ydataPar = ProcessParameter("ydata", str)
        self._yerrPar = ProcessParameter("error", str, None, optional=True)
        self._usePreviousResultPar = ProcessParameter("usepreviousresult", int, 0, optional=True)
        self._useGuessingPar = ProcessParameter("useguessing", int, 0, optional=True)
        self._modelPar = ProcessParameter("model", dict)
        self._resultPar = ProcessParameter("result", str)
        self._parameters.add(self._xdataPar)
        self._parameters.add(self._ydataPar)
        self._parameters.add(self._yerrPar)
        self._parameters.add(self._usePreviousResultPar)
        self._parameters.add(self._useGuessingPar)
        self._parameters.add(self._modelPar)
        self._parameters.add(self._resultPar)
        self._noerror = False

    def initialize(self):
        self._usePreviousResult = self._usePreviousResultPar.get()
        if (self._usePreviousResult != 0):
            self._usePreviousResult = True
        else:
            self._usePreviousResult = False
        self._useGuessing = self._useGuessingPar.get()
        if (self._useGuessing != 0):
            self._useGuessing = True
        else:
            self._useGuessing = False

        self._firstguess = True
        # first set up the fit model with the given information
        # the model is a map/dictionary:
        # first level of keys are the models
        # their respective values are the parameter names which are keys themselves
        # the values of of the parameter names are the key/value pairs for the parameter hints
        self._updateModel(self._modelPar.get())

    def execute(self, data):
        # x and y data
        independentVariable = data.getData(self._xdataPar.get())
        dependentVariable = data.getData(self._ydataPar.get())
        errorname = self._yerrPar.get()
        if(errorname is None or errorname == 'None'):
            self._noerror = True
        elif (errorname == 'poisson'):
            variableWeight = np.sqrt(np.clip(dependentVariable, 0., None))
        else:
            variableWeight = 1./data.getData(errorname)
        # check if the previous result should be used OR if it's the first fit
        if not self._useGuessing and ((not self._usePreviousResult) or self._firstguess):
            try:
                self.model.params = self.model.guess(dependentVariable, x=independentVariable)
                self._firstguess = False
            except NotImplementedError:
                if isinstance(self.model, CompositeModel):
                    pass
                else:
                    print("[FitInfo]:: The current model doesn't have a guess method implemented.")
        elif self._useGuessing:
            try:
                self.model.params = self.model.gaussguess(independentVariable, dependentVariable)
            except:
                pass
        # fit the data using the guessed value
        if self._noerror:
            self._result = self.model.fit(dependentVariable, self.model.params, x=independentVariable)
        else:
            self._result = self.model.fit(dependentVariable, self.model.params, weights=variableWeight, x=independentVariable)
        data.addData(self._resultPar.get(), self._result)

    def finalize(self, data):
        pass

    def check(self, data):
        pass

    def clearPreviousData(self, data):
        data.clearCurrent(self._resultPar.get())

    def _updateModel(self, modelDict):
        mlist = []
        # the model description consists of nested dictionaries
        # first level are the models, second layer are the attributes:
        # name and as another dictionary info on the parameters of that model
        for model, mdesc in modelDict.items():
            prefix = model
            try:
                m = mdesc['modeltype']
            except KeyError:
                print("[EXCEPTION::curvefitting] Building FitModel " + str(m) + " failed. A name is mandatory!")
                exit()
            try:
                tmpparamnames = FitModels[str(m)]().param_names
                try:
                    # some fit models do not support prefixing -- check if it's only one
                    tmpmodel = FitModels[str(m)](prefix=prefix)
                except Warning:
                    if len(modelDict) is 1:
                        tmpmodel = FitModels[str(m)]()
                    else:
                        raise Warning("There is more than one model; which clashes with the requirement of no prefix allowed.")
            except KeyError:
                print("[EXCEPTION::curvefitting] Building FitModel " + str(m) + " failed, the model is undefined.")
                print("Available models are: " + repr(FitModels.keys()))
                exit()

            # look at the parameter names from the model and pick them from the dictionary
            for pname in tmpparamnames:
                try:
                    # if present get the parameter description from the config dict
                    par = mdesc[pname]
                    parname = str(prefix+pname)
                    hintdict = {}
                    # build the dict of parameter properties
                    for k, v in par.items():
                        hintdict[k] = v
                    tmpmodel.set_param_hint(parname, **hintdict)
                    self._firstguess = False
                except KeyError:
                    pass
            mlist.append(tmpmodel)
        # build the model; start with the first one and then add from the list
        self.model = mlist.pop()
        for m in mlist:
            self.model += m
        self.model.params = self.model.make_params()

    def getFitModels(self):
        return FitModels

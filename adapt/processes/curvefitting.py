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
import lmfit.models, lmfit
#~ from lmfit.models import PolynomialModel, ExponentialModel

class curvefitting(IProcess):

    def __init__(self, ptype="curvefitting"):
        super(curvefitting, self).__init__(ptype)
        self._xdataPar = ProcessParameter("xdata", str)
        self._ydataPar = ProcessParameter("ydata", str)
        self._yerrPar = ProcessParameter("error", str)
        self._modelPar = ProcessParameter("model", dict)
        self._resultPar = ProcessParameter("result", str)
        self._parameters.add(self._xdataPar)
        self._parameters.add(self._ydataPar)
        self._parameters.add(self._yerrPar)
        self._parameters.add(self._modelPar)
        self._parameters.add(self._resultPar)

    def initialize(self, data):
        # first set up the fit model with the given information
        # the model is a map/dictionary:
        # first level of keys are the models
        # their respective values are the parameter names which are keys themselves
        # the values of of the parameter names are the key/value pairs for the parameter hints
        self._extract(self._modelPar.get())

    def execute(self, data):
        independentVariable = data.getData(self._xdataPar.get())
        dependentVariable = data.getData(self._ydataPar.get())
        print(self.model)
        #~ print(self.model.param_names)
        print(self.model.param_hints)
        #~ print(independentVariable)
        #~ print(dependentVariable)
        self._result = self.model.fit(dependentVariable, x=independentVariable)
        #~ data.addData(self._resultPar.get(), self._result)
        
    def finalize(self, data):
        pass

    def check(self, data):
        pass

    def _extract(self, modelDict):
        print("EXTRACTING")
        mlist = []
        for m, mdesc in modelDict.items():
            try:
                tmpmodel = FitModels[str(m)]()
                tmpparams = tmpmodel.make_params()
                tmpparamnames = tmpmodel.param_names
            except KeyError:
                print("[EXCEPTION::curvefitting] Building FitModel " + str(m) + " failed. Is a name defined?")
                print("Available models are: " + repr(FitModels.keys()))
                exit()
            for pname in tmpparamnames:
                try:
                    par = mdesc[pname]
                    print(tmpmodel.set_param_hint(pname, **par))
                except KeyError:
                    pass
            tmpmodel.prefix=str(mdesc['name'])
            mlist.append(tmpmodel)
            print(tmpmodel.param_hints)
        self.model = mlist.pop()
        print(self.model.param_hints)
        for m in mlist:
            self.model += m
        #~ self.model.make_params()

FitModels = { "constantModel" : lmfit.models.ConstantModel,
              "linearModel" : lmfit.models.LinearModel,
              "quadraticModel" : lmfit.models.QuadraticModel,
              "gaussianModel" : lmfit.models.GaussianModel,
              "lorentzianModel" : lmfit.models.LorentzianModel,
              "psvModel" : lmfit.models.PseudoVoigtModel,
            }


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

# minimal template example

from adapt import iProcess


class curvefittingdef(iProcess.IProcessDefinition):

    def __init__(self):
        super(curvefittingdef, self).__init__()
        self._ptype = "curvefitting"
        self.createParameter("xdata", "STRING")
        self.createParameter("ydata", "STRING")
        self.createParameter("model", "STRING", optional=True)
        self.createParameter("results", "STRING")
        self.createParameter("bkgmodel", "STRING", optional=True)
        self.createParameter("onlybkg", "BOOL", optional=True)

class curvefitting(iProcess.IProcess):

    def __init__(self, procDef):
        super(curvefitting, self).__init__(procDef)

    def initialize(self, data):
        self._xdata = self._parameters["xdata"]
        self._ydata = self._parameters["ydata"]
        self._fitmodel = self._parameters["model"]
        self._bkgonly = self._parameters["onlybkg"]
        self._bkgmodel = self._parameters["bkgmodel"]
        self._resultsname = self._parameters["results"]
        
        if self._fitmodel:
            try:
                self._model = fitModels[self._fitmodel]
            except KeyError:
                raise NotImplementedError("Missing implementation of " + 
                                  self._fitmodel + " in curvefitting." )
        
        if self._parameters["bkgmodel"]:
            try:
                self._bkgmodel = fitModels[self._parameters["bkgmodel"]]
                self._bkgmodel.prefix += "BKG_"
            except KeyError:
                raise NotImplementedError("Missing implementation of " + 
                    self._parameters["bkgmodel"] + " in curvefitting." )
        
        if not self._bkgonly and self._bkgmodel:
            self._fitmodel += self._bkgmodel

        self_fitparameters = self._model.make_params()

    def execute(self, data):
        independentVariable = data.getData(self._xdata)
        dependentVariable = data.getData(self._ydata)
        self._result = self._model.fit(dependentVariable, x=independentVariable)
        
        data.addData(self._resultsname, self._result)
        
        data.info()

    def finalize(self, data):
        pass

    def check(self, data):
        pass


# just some convenience definitions to make processing provenance easier

from lmfit import  Model
from lmfit.models import PseudoVoigtModel, LorentzianModel, GaussianModel
from lmfit.models import ConstantModel, LinearModel, QuadraticModel
#~ from lmfit.models import PolynomialModel, ExponentialModel

# the simple ones
constantModel = ConstantModel(prefix="const_")
linearModel = LinearModel(prefix="lin_")
quadraticModel = QuadraticModel(prefix="square_")

# peak like models:
gaussianModel = GaussianModel(prefix="g_")
doubleGaussianModel = GaussianModel(prefix="g1_") + GaussianModel(prefix="g2_")
tripleGaussianModel = GaussianModel(prefix="g1_") + GaussianModel(prefix="g2_") + GaussianModel(prefix="g3_")

lorentzianModel = LorentzianModel(prefix="lor_")
doubleLorentzianModel = LorentzianModel(prefix="lor1_") + LorentzianModel(prefix="lor2_")

pseudoVoigtModel = PseudoVoigtModel(prefix="psv_")

fitModels = { "constantModel" : constantModel,
              "linearModel" : linearModel,
              "quadraticModel" : quadraticModel,
              "gaussianModel" : gaussianModel,
              "doubleGaussianModel" : doubleGaussianModel,
              "tripleGaussianModel" : tripleGaussianModel,
              "lorentzianModel" : lorentzianModel,
              "doubleLorentzianModel" : doubleLorentzianModel,
              "psvModel" : pseudoVoigtModel,
            }

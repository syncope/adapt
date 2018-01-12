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
        #~ ProcessParameter("bkgmodel", "STRING", optional=True)
        #~ ProcessParameter("onlybkg", "BOOL", optional=True)
        #~ ProcessParameter("tryguessing", "BOOL", optional=True)
        #~ self._xdata = self._parameters["xdata"]
        #~ self._ydata = self._parameters["ydata"]
        #~ self._fitmodel = self._parameters["model"]
        #~ self._bkgonly = self._parameters["onlybkg"]
        #~ self._bkgmodel = self._parameters["bkgmodel"]
        #~ self._resultsname = self._parameters["result"]
        #~ self._trytoguess = self._parameters["tryguessing"]
        #~ for stuff in self._model:
        #~ print(str(self._model))
        
    def initialize(self, data):
        # first set up the fit model with the given information
        # the model is a map/dictionary:
        # first level of keys are the models
        # their respective values are the parameter names which are keys themselves
        # the values of of the parameter names are the key/value pairs for the parameter hints
        
        self.model = self._modelPar.get()
        print(str(self.model))
        #~ if self._fitmodel:
            #~ try:
                #~ self._model = fitModels[self._fitmodel]
            #~ except KeyError:
                #~ raise NotImplementedError("Missing implementation of " + 
                                  #~ self._fitmodel + " in curvefitting." )
        #~ 
        #~ if self._parameters["bkgmodel"]:
            #~ try:
                #~ self._bkgmodel = fitModels[self._parameters["bkgmodel"]]
                #~ self._bkgmodel.prefix += "BKG_"
            #~ except KeyError:
                #~ raise NotImplementedError("Missing implementation of " + 
                    #~ self._parameters["bkgmodel"] + " in curvefitting." )
        #~ 
        #~ if not self._bkgonly and self._bkgmodel:
            #~ self._fitmodel += self._bkgmodel
#~ 
        #~ self._fitparameters = self._model.make_params()

    def execute(self, data):
        pass
        #~ independentVariable = data.getData(self._xdata)
        #~ dependentVariable = data.getData(self._ydata)
        #~ if self._trytoguess:
            #~ if self._fitmodel == "gaussianModel":
                #~ meanval = np.mean(independentVariable)
                #~ amp_obs = np.amax(dependentVariable)
                #~ stderr_obs = np.std(independentVariable)
                #~ self._model.set_param_hint("g_center", value=meanval)
                #~ self._model.set_param_hint("g_amplitude", value=amp_obs)
                #~ self._model.set_param_hint("g_sigma", value=stderr_obs)
            #~ else:
                #~ try:
                    #~ self._fitparameters = self._model.guess(data=[independentVariable, dependentVariable])
                #~ except NotImplementedError:
                    #~ print("[curvefitting] Guessing is not implemented for " + str(self._model) + ".")
#~ 
        #~ self._result = self._model.fit(dependentVariable, x=independentVariable)
        #~ data.addData(self._resultsname, self._result)
        
    def finalize(self, data):
        pass

    def check(self, data):
        pass


class fitParameter():
    '''Abstract definition of a fit parameter interface.'''

    def __init__(self, obj):
        '''Also serves as a check: there must be five components!'''
        try:
            self._name = obj["name"]
            self._value = obj["value"]
            self._variable = obj["variable"]
            self._min = obj["min"]
            self._max = obj["max"]
        except KeyError("[fitParameter] The parameter is not fully qualified, at least one element is missing."):
            exit()

    def name(self):
        return self._name
    
    def value(self):
        return self._value

    def variable(self):
        return self._variable

    def min(self):
        return self._min

    def max(self):
        return self._max

    def dump(self):
        print("[fitParameter::dump]: name:" + str(self._name) 
                                + " value:" + str(self._value)
                                + " variable?" + str(self._variable)
                                + " min:" + str(self._min)
                                + " max:" + str(self._max))



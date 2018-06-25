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

# perform trapezoidal integration on the given dataset

import numpy as np
from math import fabs
try:
    from scipy.interpolate import interp1d
except ImportError:
    print("Trapezoidal integration needs scipy for interpolation; which is missing. Please install.")
    pass

from adapt.iProcess import *


class trapezoidintegration(IProcess):

    def __init__(self, ptype="trapezoidintegration"):
        super(trapezoidintegration, self).__init__(ptype)
        self._observablePar = ProcessParameter("observable", str)
        self._independentvarPar = ProcessParameter("motor", str)
        self._outputPar = ProcessParameter("output", str)
        self._parameters.add(self._observablePar)
        self._parameters.add(self._independentvarPar)
        self._parameters.add(self._outputPar)

    def initialize(self):
        self._observable = self._observablePar.get()
        self._independentvar = self._independentvarPar.get()
        self._output = self._outputPar.get()

    def execute(self, data):
        motor = data.getData(self._independentvar)
        observable = data.getData(self._observable)

        # calculate trapezoid sum
        integral=0
        for point in range(0,len(motor)-1):
            integral=integral+0.5*(observable[point+1]+observable[point])*fabs(motor[point+1]-motor[point])

        #  estimate error bar
        try:
            fn10 = interp1d(motor, observable, kind='cubic')
        except np.linalg.linalg.LinAlgError:
            # there is an error ocurring, which I don't understand. 
            # fix code for now as circumvention
            print("[trapInt]: Matrix inversion error while trying to interpolate. Trying to continue.")
            data.addData(self._output, [integral, integral])
            return

        xnew = np.linspace(motor[0], motor[len(motor)-1], 10*len(motor))
        fnew = fn10(xnew)
        integraln10=0
        for p in range(0,len(xnew)-1):
            integraln10=integraln10+0.5*(fnew[p+1]+fnew[p])*fabs(xnew[p+1]-xnew[p])
        integral_stderr=integraln10-integral
        	
        data.addData(self._output, [integral, integral_stderr])

    def finalize(self, data):
        pass

    def check(self, data):
        pass

    def clearPreviousData(self, data):
        data.clearCurrent(self._output)

# Copyright (C) 2019  Christoph Rosemann, DESY, Notkestr. 85, D-22607 Hamburg
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

# integrate a fitted model for the given fit result

from adapt.iProcess import *


class integratefitresult(IProcess):

    def __init__(self, ptype="integratefitresult"):
        super(integratefitresult, self).__init__(ptype)
        self._xdataPar = ProcessParameter("xdata", str, optional=True)
        self._fitresultPar = ProcessParameter("fitresult", str)
        self._lowlimPar = ProcessParameter("lowerbound", float, optional=True)
        self._uplimPar = ProcessParameter("upperbound", float, optional=True)
        self._parameters.add(self._xdataPar)
        self._parameters.add(self._fitresultPar)
        self._parameters.add(self._lowlimPar)
        self._parameters.add(self._uplimPar)
        self._parameters.add(self._outputPar)

    def initialize(self):
        self._xdata = self._xdataPar.get()
        self._fitresult = self._fitresultPar.get()
        self._lowlim = self._lowlimPar.get()
        self._uplim = self._uplimPar.get()
        self._output = self._outputPar.get()

    def execute(self, data):
        # first get the current fit result
        fitresult = data.getData(self._fitresult)
        xdata = data.getData(self._xdata)
        import scipy.integrate as integrate
        # then calculate the integral by calling a scipy function
        # first case: numpy array is given:
        if self._xdata is not None:
            lowlim = xdata[0]
            uplim = xdata[-1]
            if lowlim > uplim:
                lowlim, uplim = uplim, lowlim
            integral = integrate.quad(lambda x: fitresult.eval(x=x), lowlim, uplim)
        elif self._lowlim is not None and self._uplim is not None:
            integral = integrate.quad(lambda x: fitresult.eval(x=x), self._lowlim, self._uplim)
        else:
            integral = (0.0, 0.0)
        data.addData(self._output, integral[0])

    def finalize(self, data):
        pass

    def check(self, data):
        pass

    def clearPreviousData(self, data):
        data.clearCurrent(self._output)

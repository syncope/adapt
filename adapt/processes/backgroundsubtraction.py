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

# one of the most simple processes subtract two np.ndarrays, store result

from adapt.iProcess import *

class backgroundsubtraction(IProcess):

    def __init__(self, ptype="backgroundsubtraction"):
        super(backgroundsubtraction, self).__init__(ptype)
        self._inPar = ProcessParameter("input", str)
        self._outPar = ProcessParameter("output", str)
        self._bkgPar = ProcessParameter("background", str)
        self._parameters.add(self._inPar)
        self._parameters.add(self._outPar)
        self._parameters.add(self._bkgPar)

    def initialize(self):
        self._in = self._inPar.get()
        self._output = self._outPar.get()
        self._bkg = self._bkgPar.get()

    def execute(self, data):
        element = data.getData(self._in)
        background = data.getData(self._bkg)
        
        data.addData(self._output, (element - background))

    def finalize(self, data):
        pass

    def check(self, data):
        pass

    def clearPreviousData(self, data):
        data.clearCurrent(self._output)

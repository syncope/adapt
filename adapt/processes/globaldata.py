# Copyright (C) 2016  Christoph Rosemann, DESY, Notkestr. 85, D-22607 Hamburg
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


class globaldata(IProcess):

    def __init__(self, ptype="globaldata"):
        super(globaldata, self).__init__(ptype)
        self._lambdaPar = ProcessParameter("wavelength", float, optional=True)
        self._sddPar = ProcessParameter("sdd", float, optional=True)
        self._unitPar = ProcessParameter("unit", str, optional=True)
        self._parameters.add(self._lambdaPar)
        self._parameters.add(self._sddPar)
        self._parameters.add(self._unitPar)

    def initialize(self, data):
        self._lambda = self._lambdaPar.get()
        self._sdd = self._sddPar.get()
        self._unit = self._unitPar.get()
        data.addGlobalData("wavelength", self._lambda)
        data.addGlobalData("sdd", self._sdd)
        data.addGlobalData("unit", self._unit)

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

# this is a first shot at a "line integration" tool

import numpy as np

from adapt.iProcess import *


class sliceprojection(IProcess):

    def __init__(self, ptype="sliceprojection"):
        super(sliceprojection, self).__init__(ptype)
        self._inputPar = ProcessParameter("input", str)
        self._datanamePar = ProcessParameter("dataname", str)
        self._xminPar = ProcessParameter("fastmin", int)
        self._xmaxPar = ProcessParameter("fastmax", int)
        self._yminPar = ProcessParameter("slowmin", int)
        self._ymaxPar = ProcessParameter("slowmax", int)
        self._horizontalPar = ProcessParameter("horizontal", bool, True)
        self._custommaskPar = ProcessParameter("custommask", str, optional=True)
        self._parameters.add(self._inputPar)
        self._parameters.add(self._datanamePar)
        self._parameters.add(self._xminPar)
        self._parameters.add(self._xmaxPar)
        self._parameters.add(self._yminPar)
        self._parameters.add(self._ymaxPar)
        self._parameters.add(self._horizontalPar)
        self._parameters.add(self._custommaskPar)

    def initialize(self):
        self._input = self._inputPar.get()
        self._dataname = self._datanamePar.get()
        self._xmin = self._xminPar.get()
        self._xmax = self._xmaxPar.get()
        self._ymin = self._yminPar.get()
        self._ymax = self._ymaxPar.get()
        self._horizontal = self._horizontalPar.get()
        if(self._horizontal):
            self._axis = 0
        else:
            self._axis = 1
        try:
            self._custommask = self._custommaskPar.get()
        except KeyError:
            pass

    def execute(self, data):
        # fetch data and slice to the given pixels
        sliced = data.getData(
            self._input)[
                self._xmin:self._xmax,
                self._ymin:self._ymax]
        # if defined, also apply the custom mask
        try:
            sliced_mask = data.getData(self._custommask)[
                self._xmin:self._xmax, self._ymin:self._ymax]
        except AttributeError:
            pass
            # apply mask !
        # use the helper function ndarray.sum to sum in a given direction
        # use the helper function ndarray.average to average in a given direction
        # ! can use weighting as well!
        summed_masked_slice = np.average(sliced, axis=self._axis)
        data.addData(self._dataname, summed_masked_slice)

        # MISSING!! : store the start pixels as well ! -> space conversion

    def finalize(self, data):
        pass

    def check(self, data):
        pass

if __name__ == "__main__":
    s = sliceprojection()
    for p, k in s._parameters.items():
        print(p + " with name " + k._name)

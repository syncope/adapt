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
from adapt import iProcess


class sliceprojectiondef(iProcess.IProcessDefinition):

    def __init__(self):
        super(sliceprojectiondef, self).__init__()
        # define name of in- and output data
        self._ptype = "sliceprojection"
        self.createParameter("output", "STRING")
        self.createParameter("input", "STRING")
        # minimal information: x, dx, y, dy, projection direction
        self.createParameter("slowmin", "INT")
        self.createParameter("slowmax", "INT")
        self.createParameter("fastmin", "INT")
        self.createParameter("fastmax", "INT")
        self.createParameter("horizontal", "BOOL", True)
        # additional info: mask
        self.createParameter("custommask", "STRING", optional=True)

class sliceprojection(iProcess.IProcess):

    def __init__(self, pparameters):
        super(sliceprojection, self).__init__(pparameters)

    def initialize(self, data):
        self._input = self.getParameterValue("input")
        self._dataname = self.getParameterValue("dataname")
        self._xmin = self.getParameterValue("fastmin")
        self._xmax = self.getParameterValue("fastmax")
        self._ymin = self.getParameterValue("slowmin")
        self._ymax = self.getParameterValue("slowmax")
        if(self.getParameterValue("horizontal")):
            self._axis = 0
        else:
            self._axis = 1
        try:
            self._custommask = self.getParameterValue("custommask")
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

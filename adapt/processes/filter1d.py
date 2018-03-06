# Copyright (C) 2017  Christoph Rosemann, DESY, Notkestr. 85, D-22607 Hamburg
# additional author: S. Francoual, DESY,
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

# 1d filtering process -- signal shaping

import scipy.signal
import numpy as np

from adapt.iProcess import *


def medianfilter1d(data):
    return scipy.signal.medfilt(data, kernel_size=3)


class filter1d(IProcess):

    def __init__(self, ptype="filter1d"):
        super(filter1d, self).__init__(ptype)
        self._inputPar = ProcessParameter("input", str)
        self._outputPar = ProcessParameter("output", str)
        self._methodPar = ProcessParameter("method", str)
        self._parameters.add(self._inputPar)
        self._parameters.add(self._outputPar)
        self._parameters.add(self._methodPar)

        self._methods = ["medianFilter", "p09despiking"]

    def initialize(self):
        self._input = self._inputPar.get()
        self._output = self._outputPar.get()
        self._method = self._methodPar.get()
        if self._method in self._methods:
            return True
        else:
            raise NameError("Unknown method in filter1d process.")

    def execute(self, data):
        values = data.getData(self._input)
        if self._method == "medianFilter":
            data.addData(self._output, medianfilter1d(values))
        elif self._method == "p09despiking":
            data.addData(self._output, self._p09despiking(values))
        else:
            raise NameError("Some wrong method is used in filtering.")

    def finalize(self, data):
        pass

    def check(self, data):
        pass

    def _p09rolling_window(self, data, window):
        shape = data.shape[:-1] + (data.shape[-1] - window + 1, window)
        strides = data.strides + (data.strides[-1],)
        return np.lib.stride_tricks.as_strided(data, shape=shape, strides=strides)

    def _testp09despiker(self, arr):
        n1 = 1
        n2 = 1
        block = 6
        data = np.copy(arr)
        roll = self._p09rolling_window(data, block)
        roll = np.ma.masked_invalid(roll)
        std = n1 * roll.std(axis=1)
        mean = roll.mean(axis=1)
        # Use the last value to fill-up
        std = np.r_[std, np.tile(std[-1], block - 1)]
        mean = np.r_[mean, np.tile(mean[-1], block - 1)]
        mask = (np.abs(data - mean.filled(fill_value=np.NaN))
                > std.filled(fill_value=np.NaN))
        data[mask] = np.NaN
        # Pass two: recompute the mean and std without the flagged values from pass
        # one now removing the flagged data
        roll = self._p09rolling_window(data, block)
        roll = np.ma.masked_invalid(roll)
        std = n2 * roll.std(axis=1)
        mean = roll.mean(axis=1)
        # Use the last value to fill-up.
        std = np.r_[std, np.tile(std[-1], block - 1)]
        mean = np.r_[mean, np.tile(mean[-1], block - 1)]
        mask = (np.abs(arr - mean.filled(fill_value=np.NaN))
                > std.filled(fill_value=np.NaN))
        # arr[mask] = np.NaN
        return mask

    def _p09despiking(self, inputarr):
        # routine from S. Francoual, DESY,
        derivative = np.diff(inputarr, n=1)
        maskeddata = self._testp09despiker(derivative)

        if len(np.where(maskeddata)) == 0:
            return inputarr
        else:
            return medianfilter1d(inputarr)

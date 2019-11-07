# Copyright (C) 2017-9  Christoph Rosemann, DESY, Notkestr. 85, D-22607 Hamburg
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

# implement subsequence selections, needs an interface: func(seq, ...)

import numpy as np

from adapt.iProcess import *


class subsequenceselection(IProcess):

    def __init__(self, ptype="subsequenceselection"):
        super(subsequenceselection, self).__init__(ptype)
        self._inputsPar = ProcessParameter("input", list)
        self._outputPar = ProcessParameter("output", list)
        self._selectionmethodsPar = ProcessParameter("selectors", list)
        self._startpointsPar = ProcessParameter("startpointnumber", int, None, optional=True)
        self._endpointsPar = ProcessParameter("endpointnumber", int, None, optional=True)
        self._slicestartPar = ProcessParameter("slicestart", int, None, optional=True)
        self._sliceendPar = ProcessParameter("sliceend", int, None, optional=True)
        self._slicestridePar = ProcessParameter("slicestride", int, None, optional=True)
        self._parameters.add(self._inputsPar)
        self._parameters.add(self._outputPar)
        self._parameters.add(self._selectionmethodsPar)
        self._parameters.add(self._startpointsPar)
        self._parameters.add(self._endpointsPar)
        self._parameters.add(self._slicestartPar)
        self._parameters.add(self._sliceendPar)
        self._parameters.add(self._slicestridePar)

        self._methodDict = {"selectfromstart": self._selectFromStart,
                            "selectfromend": self._selectFromEnd,
                            "selectslice": self._slice,
                            }

    def initialize(self):
        self._inputs = self._inputsPar.get()
        self._output = self._outputPar.get()
        self._selectionmethods = self._selectionmethodsPar.get()
        self._startpoints = self._startpointsPar.get()
        self._endpoints = self._endpointsPar.get()
        self._slicestart = self._slicestartPar.get()
        self._sliceend = self._sliceendPar.get()
        self._slicestride = self._slicestridePar.get()

        # check if the methods are available and parameter logic is correct
        for method in self._selectionmethods:
            if method not in self._methodDict:
                raise NotImplementedError("[subsequenceselection] Method " + str(method) + " not implemented.")
        try:
            if len(self._inputs) != len(self._output):
                raise ValueError("[subsequenceselection] The number of inputs and outputs does not match.")
            if "selectfromstart" in self._selectionmethods and not self._startpoints:
                raise ValueError("[subsequenceselection] Method selectfromstart needs a startpointnumber.")
            if "selectfromend" in self._selectionmethods and not self._endpoints:
                raise ValueError("[subsequenceselection] Method selectfromend needs a endpointnumber.")
            if "selectslice" in self._selectionmethods and (self._slicestart is None or self._sliceend is None):
                raise ValueError("[subsequenceselection] Method selectslice needs start and end values.")
            if "selectslice" in self._selectionmethods and len(self._selectionmethods) > 1:
                raise ValueError("[subsequenceselection] Method selectslice cannot be combined with another selection method.")
        except:
            pass

    def execute(self, data):
        # start or endselection:
        if "selectfromstart" in self._selectionmethods or "selectfromend" in self._selectionmethods:
            for index in range(len(self._inputs)):
                sequence = data.getData(self._inputs[index])
                tempout = []
                if "selectfromstart" in self._selectionmethods:
                    tmp = self._selectFromStart(sequence, self._startpoints)
                    tempout.append(self._selectFromStart(sequence, self._startpoints))
                if "selectfromend" in self._selectionmethods:
                    tmp = self._selectFromEnd(sequence, self._endpoints)
                    tempout.append(self._selectFromEnd(sequence, self._endpoints))
                # if "selectSection" in self._selectionmethods:
                    # tempout.append(self._selectSection(sequence, self._startendindices))
                out = tempout[0]
                for elem in tempout[1:]:
                    out = np.concatenate((out, elem))
                data.addData(self._output[index], out)
        elif "selectslice" in self._selectionmethods:
            for index in range(len(self._inputs)):
                sequence = data.getData(self._inputs[index])

    def finalize(self, data):
        pass

    def check(self, data):
        pass

    def clearPreviousData(self, data):
        data.clearCurrent(self._output)

    def _selectFromStart(self, seq, num):
        '''create a subsequence that only has the first num elements of seq'''
        return seq[:num]

    def _selectFromEnd(self, seq, num):
        '''create a subsequence that only has the last num elements of seq'''
        return seq[(-1)*num:]

    def _slice(self, seq):
        pass

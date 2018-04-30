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

# implement subsequence selections, needs an interface: func(seq, ...)

import numpy as np

from adapt.iProcess import *


class subsequenceselection(IProcess):
    
    def __init__(self, ptype="subsequenceselection"):
        super(subsequenceselection, self).__init__(ptype)
        self._inputsPar = ProcessParameter("input", list)
        self._outputPar = ProcessParameter("output", list)
        self._selectionmethodsPar = ProcessParameter("selectors", list)
        self._startpointsPar = ProcessParameter("startpointnumber", int, optional=True)
        self._endpointsPar = ProcessParameter("endpointnumber", int, optional=True)
        #~ self._startendindicesPar = ProcessParameter("startendindices", list, optional=True)
        self._parameters.add(self._inputsPar)
        self._parameters.add(self._outputPar)
        self._parameters.add(self._selectionmethodsPar)
        self._parameters.add(self._startpointsPar)
        self._parameters.add(self._endpointsPar)
        #~ self._parameters.add(self._startendindicesPar)
        self._methodDict = {"selectfromstart" : self._selectFromStart,
                            "selectfromend" : self._selectFromEnd,
                            #~ "selectSection" : self._selectSection,
                           }

    def initialize(self):
        self._inputs = self._inputsPar.get()
        self._output = self._outputPar.get()
        self._selectionmethods = self._selectionmethodsPar.get()
        self._startpoints = self._startpointsPar.get()
        self._endpoints = self._endpointsPar.get()
        #~ self._startendindices = self._startendindicesPar.get()

        # check if the methods are available and parameter logic is correct
        for method in self._selectionmethods:
            if method not in self._methodDict:
                raise NotImplementedError("[subsequenceselection] Method " 
                + str(method) + " not implemented.")
        if len(self._inputs) != len(self._output):
            raise ValueError("[subsequenceselection] The number of inputs and outputs does not match.")
        if "selectfromstart" in self._selectionmethods and not self._startpoints:
            raise ValueError("[subsequenceselection] Method selectfromstart needs a startpointnumber.")
        if "selectfromend" in self._selectionmethods and not self._endpoints:
            raise ValueError("[subsequenceselection] Method selectfromend needs a endpointnumber.")
        #~ if "selectSection" in self._selectionmethods and not self._startendindices:
            #~ raise ValueError("[subsequenceselection] Method selectSection needs startendindices.")

    def execute(self, data):
        # outer loop: over the inputs
        for index in range(len(self._inputs)):
            sequence = data.getData(self._inputs[index])
            tempout = []
            if "selectfromstart" in self._selectionmethods:
                tmp = self._selectFromStart(sequence, self._startpoints)
                tempout.append(self._selectFromStart(sequence, self._startpoints))
            if "selectfromend" in self._selectionmethods:
                tmp = self._selectFromEnd(sequence, self._endpoints)
                tempout.append(self._selectFromEnd(sequence, self._endpoints))
            #~ if "selectSection" in self._selectionmethods:
                #~ tempout.append(self._selectSection(sequence, self._startendindices))
            out = tempout[0]
            for elem in tempout[1:]:
                out = np.concatenate((out, elem))
            data.addData(self._output[index], out)

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
    
    #~ def _selectSection(self, seq, indices=[0,-1]):
        #~ return seq[indices[0]:indices[1]]

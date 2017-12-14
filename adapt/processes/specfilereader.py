# Copyright (C) 2017  Christoph Rosemann, DESY, Notkestr. 85, D-22607 Hamburg
# email contact: christoph.rosemann@desy.de
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation in version 2
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


# general idea:
# a) read in the file, decompose into individual scans:
#    !!! the separation is asserted to be a blank line !!!
# b) create a list of raw scan objects 
# c) convert the raw objects into scan data objects


import logging
logger = logging.getLogger('adapt.log')

import numpy as np
try:
    from cStringIO import StringIO # StringIO behaves like a file object
except ImportError: # no more StringIO in Python3 -> different module
    from io import StringIO

from adapt.iProcess import *


class specfilereader(IProcess):

    def __init__(self, ptype="specfilereader"):
        super(specfilereader, self).__init__(ptype)

        self._in = ProcessParameter("filename", str)
        self._out = ProcessParameter("outputdata", str)
        self._startScan = ProcessParameter("startScan", int)
        self._endScan = ProcessParameter("endScan", int)
        self._stride = ProcessParameter("stride", int, 1, optional=True)
        self._parameters.add(self._in)
        self._parameters.add(self._out)
        self._parameters.add(self._startScan)
        self._parameters.add(self._endScan)
        self._parameters.add(self._stride)

    def initialize(self, data):
        self.sfr = SpecFileReader(self._in.get())
        if self._stride != 1:
            self.scandata = self.sfr.read(self._startScan.get(),
                                          self._endScan.get(),
                                          self._stride.get())
        else:
            self.scandata = self.sfr.read(self._startScan.get(),
                                          self._endScan.get())
        self.dataIterator = iter(self.scandata)

    def execute(self, data):
        # read next entry from spec file, 
        # put scandata object to common memory
        try:
            data.addData(self._out.get(), next(self.dataIterator))
        except StopIteration:
            print("---End of procesing ---")
            raise StopIteration

    def finalize(self, data):
        pass

    def check(self, data):
        pass


class SpecFileReader():
    def __init__(self, fname):
        self._fname = fname
        self._rawScanList = []
        self._scanList = []
        self._scanDataList = []

    def read(self, start=None, end=None, stride=1):
        try:
            _file = open(self._fname, 'r')
        except(IOError):
            logger.error("[SpecFileReader]: File " + str(self._fname) + " can't be opened for reading.")

        # start iteration to create individual scan objects
        nextScan = _rawScan()
        for line in _file:
            if line in ['\n', '\r\n']:
                if nextScan is not None:
                    self._rawScanList.append(nextScan)
                    nextScan = _rawScan()
            else:
                nextScan.addLine(line)
        if nextScan is not None:
            self._rawScanList.append(nextScan)

        # convert the raw objects into scan data
        for rawS in self._rawScanList:
            # only take the ones into account where the stride is right
            if self._rawScanList.index(rawS) % stride:
                continue
            converted = rawS.convertToScanData()
            if converted is not None:
                if self.checkValidScanID(converted.getScanNumber(), start, end):
                    self._scanDataList.append(converted)

        return self._scanDataList

    def checkValidScanID(self, scanNumber, start, end):
        if start is None and end is None:
            return True
        elif start is not None and end is None:
            return scanNumber >= start
        elif start is None and end is not None:
            return scanNumber <= end
        elif start is not None and end is not None:
            return (scanNumber >= start) and (scanNumber <= end)

class _rawScan():
    '''Placeholder object for disassembling the spec file'''

    def __init__(self):
        self._lines = []
        self._dataString = ""

    def addLine(self, line):
        self._lines.append(line)
        if line.split(' ')[0][0] != '#':
           self._dataString += line

    def convertToScanData(self):
        '''Create the scanData object from the raw file objects.'''
        # get the different comment fields, as specified
        sd = SpecFileScanData()
        rawKeys = []
        rawValues = []
        for line in self._lines:
            words = line.rstrip('\n')
            splitWords = words.split(' ')
            keyword = splitWords[0]
            if keyword == '#S':
                sd.setStartline(splitWords[1:])
            elif keyword == '#U':
                sd.setUsername(splitWords[1:])
            elif keyword == '#D':
                sd.setDate(splitWords[1:])
            elif keyword == '#C':
                sd.addComment(splitWords[1:])
            elif keyword == '#N':
                sd.setNumberOfColumns(splitWords[1])
            elif keyword == '#L':
                for w in splitWords[1:]:
                    if w != '':
                        sd.addLabel(w)
            elif keyword[0:2] == '#O':
                for w in splitWords[1:]:
                    if w != '':
                        rawKeys.append(w)
            elif keyword[0:2] == '#P':
                for w in splitWords[1:]:
                    if w != '':
                        rawValues.append(w)

        sd.addCustomdataDict({rawKeys[i]: float(rawValues[i]) for i in range(len(rawValues))})

        # check if everything is there
        if not sd.checkSanity():
            return

        labels = sd.getLabels()
        noc = sd.getNumberOfColumns()

        if(self._dataString == ''):
            logger.info("[SpecFileReader] No data to read in scan number " + str(sd.getScanNumber()))
            return None

        # get the data into numpy arrays
        sio = StringIO(self._dataString)

        multi = np.loadtxt(sio, unpack=True)
        sd.addDataDict( {labels[i]: multi[i] for i in range(noc) } )
        sd.addLabelDict( {i: labels[i] for i in range(noc) } )

        return sd


class SpecFileScanData():
    '''This is the atomic data exchange object. It consists of all
       information that is nneded for a scan.'''
    
    def __init__(self):
        self._startline = ''
        self._number = 0
        self._username = ''
        self._date = ''
        self._comments = []
        self._customdata = {}
        self._noc = 0
        self._labels = []
        self._dataDict = {}
        self._labelDict = {}

    def getScanNumber(self):
        return self._number

    def getLabels(self):
        return self._labels

    def getNumberOfColumns(self):
        return self._noc

    def getArray(self, key):
        return self._dataDict[key]

    def getCustomKeys(self):
        return self._customdata.keys()
    
    def getCustomVar(self, key):
        return self._customdata[key]

    def setStartline(self, sl):
        self._startline = sl
        self.setScanNumber(int(sl[0]))

    def setScanNumber(self, number):
        self._number = int(number)

    def setUsername(self, username):
        self._username = username

    def setDate(self, date):
        self._date = date
    
    def addComment(self, comment):
        self._comments.extend(comment)

    def addCustomdataDict(self, dic):
        self._customdata = dic

    def setNumberOfColumns(self, noc):
        self._noc = int(noc)

    def addLabel(self, label):
        self._labels.append(label)

    def addDataDict(self, dic):
        self._dataDict = dic 

    def addLabelDict(self, dic):
        self._labelDict = dic 

    def checkSanity(self):
        '''Tests whether the minimal requirements are met.'''
        if ( self._noc is not len(self._labels)):
            return False
        return (self._startline and self._labels and self._noc)

    def dump(self):
        print (" values are: ")
        print(self._startline)
        print(self._number)
        print(self._username)
        print(self._date)
        print(self._comments)
        print(self._customdata)
        print(self._noc)
        print(self._labels)
        print(self._dataDict)

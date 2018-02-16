# Copyright (C) 2018  Christoph Rosemann, DESY, Notkestr. 85, D-22607 Hamburg
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

# pure data class as helper for the iint gui

class IintData():

    def __init__(self, scanid, scantype, motor):
        self._id = scanid
        self._typeName = scantype
        self._motorName = motor
        self._hasRaw = False
        self._hasMotor = False
        self._hasObservable = False
        self._hasDespiked = False
        self._hasBackground = False
        self._hasBKGsub = False
        self._hasFit = False
        self._hasIntegration = False
        self._raw = None
        self._motor = None
        self._observable = None
        self._despikedObservable = None
        self._fittedBackground = None
        self._backgroundSubtracted = None
        self._fittedSignal = None
        self._integratedIntensity = None

    def getScanID(self):
        return self._id

    def getScanType(self):
        return self._typeName

    def getMotorName(self):
        return self._motorName

    def setRaw(self, rd):
        self._raw = rd
        self._hasRaw = True

    def getRaw(self):
        if(self._hasRaw):
            return self._raw
        else:
            return None

    def setMotor(self,mot):
        self._motor = mot
        self._hasMotor = True

    def getMotor(self):
        if(self._hasMotor):
            return self._motor
        else:
            return None

    def setObservable(self, obs):
        self._observable = obs
        self._hasObservable = True

    def getObservable(self):
        if(self._hasObservable):
            return self._observable
        else:
            return None

    def setDespiked(self, desp):
        self._despikedObservable = desp
        self._hasDespiked = True

    def getDespiked(self):
        if(self._hasDespiked):
            return self._despikedObservable
        else:
            return None

    def setBackground(self,bkg):
        self._fittedBackground = bkg
        self._hasBackground = True

    def getBackground(self):
        if(self._hasBackground):
            return self._fittedBackground
        else:
            return None

    def setBkgSubtracted(self,bkgsub):
        self._backgroundSubtracted = bkg
        self._hasBKGsub = True

    def getBkgSubtracted(self):
        if(self._hasBKGsub):
            return self._backgroundSubtracted
        else:
            return None

    def setSignal(self, sig):
        self._fittedSignal = sig
        self._hasFit = True

    def getSignal(self):
        if(self._hasFit):
            return self._fittedSignal
        else:
            return None

    def setIint(self, iint):
        self._integratedIntensity = iint
        self._hasIntegration = True

    def getIint(self):
        if(self._hasIntegration):
            return self._integratedIntensity
        else:
            return None

    #~ def dump(self):
        #~ print(" [ INFO ] :: my id is  " + str(self._id))
        #~ print(" my motor: " + str(self._motor))

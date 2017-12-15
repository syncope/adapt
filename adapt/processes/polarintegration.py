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

# this is a first shot at an azimuthal integrator based on pyFAI

import pyFAI

from adapt/iProcess import *


class polarintegration(IProcess):

    def __init__(self, ptype="polarintegration"):
        super(polarintegration, self).__init__(ptype)
        self._inputPar = ProcessParameter("input", str, "data")
        self._datanamePar = ProcessParameter("dataname", str, "polarintegrated")
        self._detectornamePar = ProcessParameter("detectorname", str, None)
        self._custommaskPar = ProcessParameter("custommask", str, optional=True)
        self._poni1Par = ProcessParameter("poni1", float, optional=True)
        self._poni2Par =  ProcessParameter("poni2", float, optional=True)
        self._rot1Par =  ProcessParameter("rot1", float, optional=True)
        self._rot2Par =  ProcessParameter("rot2", float, optional=True)
        self._rot3Par =  ProcessParameter("rot3", float, optional=True)
        self._fit2dstylePar =  ProcessParameter("fit2dstyle", bool, optional=True)
        self._center1Par =  ProcessParameter("center1", int, optional=True)
        self._center2Par =  ProcessParameter("center2", int, optional=True)
        self._tiltPar =  ProcessParameter("tilt", float, optional=True)
        self._tiltrotationPar =  ProcessParameter("tiltrotation", float, optional=True)
        self._nbinsPar =  ProcessParameter("nbins", int)
        self._methodPar =  ProcessParameter("method", str, "lut", optional=True)
        self._aziminPar =  ProcessParameter("azimlowlim", float, optional=True)
        self._azimaxPar =  ProcessParameter("azimhighlim", float, optional=True)
        self._rminPar =  ProcessParameter("radiallowlim", float, optional=True)
        self._rmaxPar =  ProcessParameter("radialhighlim", float, optional=True)
        self._parmaters.add(self._inputPar)
        self._parmaters.add(self._datanamePar)
        self._parmaters.add(self._detectornamePar)
        self._parmaters.add(self._custommaskPar)
        self._parmaters.add(self._poni1Par)
        self._parmaters.add(self._poni2Par)
        self._parmaters.add(self._rot1Par)
        self._parmaters.add(self._rot2Par)
        self._parmaters.add(self._rot3Par)
        self._parmaters.add(self._fit2dstylePar)
        self._parmaters.add(self._center1Par)
        self._parmaters.add(self._center2Par)
        self._parmaters.add(self._tiltPar)
        self._parmaters.add(self._tiltrotationPar)
        self._parmaters.add(self._nbinsPar)
        self._parmaters.add(self._methodPar)
        self._parmaters.add(self._aziminPar)
        self._parmaters.add(self._azimaxPar)
        self._parmaters.add(self._rminPar)
        self._parmaters.add(self._rmaxPar)

    def initialize(self, data):
        self._input = self._inputPar.get()
        self._dataname = self._datanamePar.get()
        self._nbins = self._nbinsPar.get()
        self._unit = self._unitPar.get()
        self._method = self._methodPar.get()
        _detector = self._detectornamePar.get()
        _wavelength = data.get("wavelength")
        _distance = data.get("sdd")
        
        # distinguish between fit2d and pyFAI style
        if(self._parameters["fit2dstyle"] == True):
            self._AI = pyFAI.AzimuthalIntegrator(dist=_distance,
                                                 wavelength=_wavelength,
                                                 detector=_detector)
            self._AI.setFit2D(_distance,
                              self._parameters["center1"],
                              self._parameters["center2"])
        else:
            self._AI = pyFAI.AzimuthalIntegrator(dist=_distance,
                                                 poni1=self._parameters[
                                                     "poni1"],
                                                 poni2=self._parameters[
                                                     "poni2"],
                                                 rot1=self._parameters[
                                                     "rot1"],
                                                 rot2=self._parameters[
                                                 "rot2"],
                                                 rot3=self._parameters[
                                                 "rot3"],
                                                 wavelength=_wavelength,
                                                 detector=_detector)

    def execute(self, data):
        self._AI.integrate1d(data.getData(self._input),  # data
                             npt=self._nbins, # number of points in the output pattern 
                             
                             # correctSolidAngle=True, # correct for solid angle of each pixel if True
                             # variance=None, # array containing the variance of the data. If not available, no error propagation is done
                             # radial_range=(self.getOptionalParameterValue("radiallowlim"), self.getOptionalParameterValue("radialhighlim")), # The lower and upper range of the radial unit. If not provided, range is simply (data.min(), data.max()). Values outside the range are ignored.
                             # azimuth_range=(self.getOptionalParameterValue("azimlowlim"), self.getOptionalParameterValue("azimhighlim")), # The lower and upper range of the azimuthal angle in degree. If not provided, range is simply (data.min(), data.max()). Values outside the range are ignored.
                             # mask=self.getOptionalParameterValue("custommask"), # array (same size as image) with 1 for masked pixels, and 0 for valid pixels
                             method=self._method, 
                             unit=self._unit
                             )

    def finalize(self, data):
        pass

    def check(self, data):
        pass

if __name__ == "__main__":
    s = polarintegration()
    for p, k in s._parameters.items():
        print(p + " with name " + k._name)


# create the detector for the pixel info and the mask (of present)
#~ > self._detector = pyFAI.detector_factory(self._detectorname)
#~ > self._AI = pyFAI.AzimuthalIntegrator(detector=self._detector)
#~ > self._AI = pyFAI.AzimuthalIntegrator(dist=self._sdd, poni1=self._poni1, poni2=self._poni2,
# rot1=self._rot1, rot2=self._rot2, rot3=self._rot3, splineFile=None, wavelength=None, detector=self._detector)
#~ > self._mask = self._AI.detector.mask
# add check if the detector mask exists
#~ > self._combined_mask = numpy.logical_or(self._mask, self._custom_mask).astype("int8")
#~ >
#~ > self._AI.detector.mask = self._combined_mask
# and finally put the calibration inside:
# either by fit2d method:
# self._AI.setFit2D( $sdd[mm], $pixelcenter1[int --
# pixel],pixelcenter2[int -- pixel])

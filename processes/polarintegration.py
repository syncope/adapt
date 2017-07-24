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
from adapt import iProcess


class polarintegrationdef(iProcess.IProcessDefinition):

    def __init__(self):
        super(polarintegrationdef, self).__init__()
        self._ptype = "polarintegration"
        # names of in- and output
        self.createParameter("input", "STRING", "data")
        self.createParameter("output", "STRING", "polarintegrated")

        # information about masking and detector
        self.createParameter("detectorname", "STRING", None)
        self.createParameter("custommask", "STRING", optional=True)

        # original pyfai parametrization
        self.createParameter("poni1", "FLOAT", optional=True)
        self.createParameter("poni2", "FLOAT", optional=True)
        self.createParameter("rot1", "FLOAT", optional=True)
        self.createParameter("rot2", "FLOAT", optional=True)
        self.createParameter("rot3", "FLOAT", optional=True)

        # and old-style fit2d
        self.createParameter("fit2dstyle", "BOOL", optional=True)
        self.createParameter("center1", "INT", optional=True)
        self.createParameter("center2", "INT", optional=True)
        self.createParameter("tilt", "FLOAT", optional=True)
        self.createParameter("tiltrotation", "FLOAT", optional=True)

        # now real parameters that steer the integration
        self.createParameter("nbins", "INT")
        self.createParameter("method", "STRING", value="lut", optional=True)
        self.createParameter("azimlowlim", "FLOAT", optional=True)
        self.createParameter("azimhighlim", "FLOAT", optional=True)
        self.createParameter("radiallowlim", "FLOAT", optional=True)
        self.createParameter("radialhighlim", "FLOAT", optional=True)

class polarintegration(iProcess.IProcess):

    def __init__(self, pparameters):
        super(polarintegration, self).__init__(pparameters)

    def initialize(self, data):
        self._input = self._parameters["input"]
        self._dataname = self._parameters["output"]
        self._nbins = self._parameters["nbins"]
        self._unit = data.getData("unit")
        self._method = self._parameters["method"]
        _detector = self._parameters["detectorname"]
        _wavelength = data.getData("wavelength")
        _distance = data.getData("sdd")
        
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
                             # error_model="poisson", # When the variance is unknown, an error model can be given: “poisson” (variance = I), “azimuthal” (variance = (I-<I>)^2)
                             # radial_range=(self.getOptionalParameterValue("radiallowlim"), self.getOptionalParameterValue("radialhighlim")), # The lower and upper range of the radial unit. If not provided, range is simply (data.min(), data.max()). Values outside the range are ignored.
                             # azimuth_range=(self.getOptionalParameterValue("azimlowlim"), self.getOptionalParameterValue("azimhighlim")), # The lower and upper range of the azimuthal angle in degree. If not provided, range is simply (data.min(), data.max()). Values outside the range are ignored.
                             # mask=self.getOptionalParameterValue("custommask"), # array (same size as image) with 1 for masked pixels, and 0 for valid pixels
                             # polarization_factor (float) – polarization factor between -1 (vertical) and +1 (horizontal). 0 for circular polarization or random, None for no correction
                             method=self._method, # # can be “numpy”, “cython”, “BBox” or “splitpixel”, “lut”, “csr”, “nosplit_csr”, “full_csr”, “lut_ocl” and “csr_ocl” if you want to go on GPU. To Specify the device: “csr_ocl_1,2”
                             unit=self._unit # Output units, can be “q_nm^-1”, “q_A^-1”, “2th_deg”,
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

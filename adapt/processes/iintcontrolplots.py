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

# small helper class for plotting specific to beamline p09 @ DESY PS

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from adapt.iProcess import *


class iintcontrolplots(IProcess):

    def __init__(self, ptype="iintcontrolplots"):
        super(iintcontrolplots, self).__init__(ptype)
        self._outputNamePar = ProcessParameter("outputname", str)
        self._rawdataPar = ProcessParameter("specdataname", str)
        self._fitresultPar = ProcessParameter("fitresult", str)
        self._trapintPar = ProcessParameter("trapintname", str)
        self._parameters.add(self._outputNamePar)
        self._parameters.add(self._rawdataPar)
        self._parameters.add(self._fitresultPar)
        self._parameters.add(self._trapintPar)

    def initialize(self):
        self._output = self._outputNamePar.get()
        self._rawdata = self._rawdataPar.get()
        self._fitresult = self._fitresultPar.get()
        self._trapint = self._trapintPar.get()
        self._storage = {}
        self._storage["temperature"] = []
        self._storage["temperature_stderr"] = []
        self._storage["magneticfield"] = []
        self._storage["magneticfield_stderr"] = []
        self._storage["trapint"] = []
        self._storage["trapint_stderr"] = []
        self._storage["amplitude"] = []
        self._storage["amplitude_stderr"] = []
        self._storage["sigma"] = []
        self._storage["sigma_stderr"] = []
        self._storage["mean"] = []
        self._storage["mean_stderr"] = []

    def execute(self, data):
        self._storage["magneticfield"].append(np.mean(data.getData(self._rawdata).getArray('lks340_outputchannela')))
        self._storage["magneticfield_stderr"].append(np.std(data.getData(self._rawdata).getArray('lks340_outputchannela')))
        self._storage["temperature"].append(np.mean(data.getData(self._rawdata).getArray('lks340_outputchannelb')))
        self._storage["temperature_stderr"].append(np.std(data.getData(self._rawdata).getArray('lks340_outputchannelb')))

        self._storage["trapint"].append(data.getData(self._trapint))
        fitresult = data.getData(self._fitresult)
        fitparams = fitresult.params
        self._storage["amplitude"].append(fitparams['m0_amplitude'].value)
        self._storage["sigma"].append(fitparams['m0_sigma'].value)
        self._storage["mean"].append(fitparams['m0_center'].value)

    def finalize(self, data):
        # the dictionary of all scan values
        inspectdata = self._storage
        fig_size = plt.rcParams["figure.figsize"]
        fig_size[0] = 16
        fig_size[1] = 12
        plt.rcParams["figure.figsize"] = fig_size

        magneticfield = np.asarray(inspectdata['magneticfield'], dtype=float)
        magneticfielderr = np.asarray(inspectdata['magneticfield_stderr'], dtype=float)
        temperature = np.asarray(inspectdata['temperature'], dtype=float)
        temperatureerr = np.asarray(inspectdata['temperature_stderr'], dtype=float)

        amplitude = np.asarray(inspectdata['amplitude'], dtype=float)
        trapint = np.asarray(inspectdata['trapint'], dtype=float)
        mean = np.asarray(inspectdata['mean'], dtype=float)
        sigma = np.asarray(inspectdata['sigma'], dtype=float)

        plt.figure(0)
        plt.subplot(3, 1, 1)
        plt.errorbar(magneticfield, amplitude, xerr=magneticfielderr, fmt='co-', ecolor='cyan', label='gaussfit')
        plt.errorbar(magneticfield, amplitude, xerr=magneticfielderr, fmt='bo-', ecolor='blue', label='iint sum')
        plt.title('Data analysis #'+str(self._output))
        plt.legend(loc=3)
        plt.subplot(3, 1, 2)
        plt.errorbar(magneticfield, mean, xerr=magneticfielderr, fmt='bo-', ecolor='blue', label='cen')
        plt.legend(loc=3)
        plt.subplot(3, 1, 3)
        plt.errorbar(magneticfield, sigma, xerr=magneticfielderr, fmt='bo-', ecolor='blue', label='cen')
        plt.legend(loc=3)
        plt.xlabel('Magnetic Field (T)')

        plt.figure(1)
        plt.subplot(3, 1, 1)
        plt.errorbar(temperature, amplitude, xerr=temperatureerr, fmt='co-', ecolor='cyan', label='gaussfit')
        plt.errorbar(temperature, amplitude, xerr=temperatureerr, fmt='bo-', ecolor='blue', label='iint sum')
        plt.legend(loc=3)
        plt.title('Data analysis #'+str(self._output))
        plt.subplot(3, 1, 2)
        plt.errorbar(temperature, mean, xerr=temperatureerr, fmt='bo-', ecolor='blue', label='cen')
        plt.legend(loc=3)
        plt.subplot(3, 1, 3)
        plt.errorbar(temperature, sigma, xerr=temperatureerr, fmt='bo-', ecolor='blue', label='cen')
        plt.legend(loc=3)
        plt.xlabel('Temperature (K)')

        output = self._output + '_controlPlots.pdf'
        with PdfPages(output) as pdf:
            for i in [0, 1]:
                pdf.savefig(plt.figure(i))
        plt.close("all")

    def check(self, data):
        pass

    def clearPreviousData(self, data):
        data.clearCurrent(self._output)

    def fitfunc(self, x, a0, a1, a2):
        return (a0/2.) * (1. + (cos(self.tthana*pi/180.))**2 + ((sin(self.tthana*pi/180.))**2) * (a1 * np.cos(2 * (x) * pi/180.) + a2 * np.sin(2 * (x) * pi/180.)))

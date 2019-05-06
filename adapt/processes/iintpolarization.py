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

# polarization analysis specific to beamline p09 @ DESY PS

import numpy as np
from scipy.optimize import curve_fit
from math import pi, cos, sin, sqrt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from adapt.iProcess import *
from adapt.adaptException import AdaptProcessException

class iintpolarization(IProcess):

    def __init__(self, ptype="iintpolarization"):
        super(iintpolarization, self).__init__(ptype)
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
        self._storage["scannumber"] = []
        self._storage["peta"] = []
        self._storage["ptth"] = []
        self._storage["pr1chi"] = []
        self._storage["pr2chi"] = []
        self._storage["trapint"] = []
        self._storage["trapint_stderr"] = []
        self._storage["gaussint"] = []
        self._storage["gaussint_stderr"] = []

    def execute(self, data):
        self._storage["scannumber"].append(int(data.getData("scannumber")))
        self._storage["peta"].append(data.getData(self._rawdata).getCustomVar('peta'))
        self._storage["ptth"].append(data.getData(self._rawdata).getCustomVar('ptth'))
        self._storage["pr1chi"].append(data.getData(self._rawdata).getCustomVar('pr1chi'))
        self._storage["pr2chi"].append(data.getData(self._rawdata).getCustomVar('pr2chi'))
        self._storage["trapint"].append(data.getData(self._trapint))
        self._storage["trapint_stderr"].append(data.getData(self._trapint + "_stderr"))
        fitresult = data.getData(self._fitresult)
        fitparams = fitresult.params
        self._storage["gaussint"].append(fitparams['m0_amplitude'].value)
        self._storage["gaussint_stderr"].append(fitparams['m0_amplitude'].stderr)

    def finalize(self, data):
        # the dictionary of all scan values
        poldata = self._storage
        fig_size = plt.rcParams["figure.figsize"]
        fig_size[0] = 16
        fig_size[1] = 12
        plt.rcParams["figure.figsize"] = fig_size

        # and finally: build the associative data block
        pr1chiana = np.unique(np.asarray(poldata["pr1chi"], dtype=float))
        pr2chiana = np.unique(np.asarray(poldata["pr2chi"], dtype=float))
        petaana = np.unique(np.asarray(poldata["peta"], dtype=float))
        self.tthana = np.mean(np.asarray(poldata["ptth"], dtype=float))
        # check if it adds up
        if len(petaana)*len(pr1chiana) != len(poldata["scannumber"]):
           # raise exception
           raise AdaptProcessException()
            #~ print("[iintPolar] Polarization analysis cannot be performed, the number of values doesn't match.")

        def getValueRangeByIndex(index):
            length = len(petaana)
            eta = np.asarray(poldata["peta"], dtype=float)[(index-1)*length:index*length]
            iint = np.asarray(poldata["trapint"], dtype=float)[(index-1)*length:index*length]
            iinterr = np.asarray(poldata["trapint_stderr"], dtype=float)[(index-1)*length:index*length]
            iintgauss = np.asarray(poldata["gaussint"], dtype=float)[(index-1)*length:index*length]
            iintgausserr = np.asarray(poldata["gaussint_stderr"], dtype=float)[(index-1)*length:index*length]
            pr2chi = np.mean(np.asarray(poldata["pr2chi"], dtype=float)[(index-1)*length:index*length])
            pr1chi = np.mean(np.asarray(poldata["pr1chi"], dtype=float)[(index-1)*length:index*length])
            polangle = 2*pr2chi
            return eta, iint, iinterr, iintgauss, iintgausserr, pr1chi, pr2chi, polangle

        i = 1
        ifig = 0
        eta, iint, iinterr, iintgauss, iintgausserr, pr1chi, pr2chi, polangle = getValueRangeByIndex(i)
        popt, pcov = curve_fit(self.fitfunc, eta, iint)
        popt, pcov = curve_fit(self.fitfunc, eta, iint)

        results = []

        for i in range(len(pr1chiana)):
            j = i + 1
            eta, iint, iinterr, iintgauss, iintgausserr, pr1chi, pr2chi, polangle = getValueRangeByIndex(j)
            # add additional check if the amplitude changes at all during fitting
            # introduced by request: fitting failes -- far too large values of amplitude
            prev = 1.0
            for k in range(10):
                if k > 0:
                    prev = popt[0]
                popt, pcov = curve_fit(self.fitfunc, eta, iint, p0=[popt[0], popt[1], popt[2]])
                if prev == popt[0] and abs(popt[0] - 10**k) < 0.01:
                    popt[0] = popt[0]*10
            fitresults = [pr1chi, pr2chi, polangle, popt[0], pcov[0, 0]**0.5, popt[1], pcov[1, 1]**0.5, popt[2], pcov[2, 2]**0.5, sqrt(popt[1]**2+popt[2]**2)]
            results.append(fitresults)

            if i % 9 == 0:
                ifig = ifig + 1
                isubpl = 1
                plt.figure(ifig)
            fig = plt.figure(ifig)
            fig.suptitle('Polarization Analysis', fontsize=14, fontweight='bold')
            plt.subplot(3, 3, isubpl)
            plt.errorbar(eta, iint, yerr=iinterr, fmt='ro', capsize=0, ls='none', color='blue', elinewidth=2, ecolor='black', label='iintsum')
            plt.errorbar(eta, iintgauss, yerr=iintgausserr, fmt='r+', capsize=0, ls='none', color='blue', elinewidth=2, ecolor='black', label='iintgauss')
            xfine = np.linspace(np.amin(petaana), np.amax(petaana), 100)  # define values to plot the function for
            plt.plot(xfine, self.fitfunc(xfine, *popt), 'r-', label='fit')
            plt.title('Scans #S'+str(int(poldata["scannumber"][(j-1)*len(petaana)]))+'_S'+str(int(poldata["scannumber"][j*len(petaana)-1]))+'\n'+' pr1chi = '+str(int(pr1chi))+'; pr2chi = '+str(int(pr2chi)), fontsize=9)
            plt.legend(fontsize=9, loc=3)
            isubpl = isubpl + 1

        b = np.vstack(results)
        for i in range(1, ifig + 1, 1):
            plt.figure(i)
        np.savetxt(self._output + '.stokes', b, fmt='%14.4f')

        fig_size[0] = 12
        fig_size[1] = 9
        plt.rcParams["figure.figsize"] = fig_size

        a = np.transpose(results)
        plt.figure(ifig+1)
        plt.errorbar(a[2], a[5], yerr=a[6], fmt='bo-', ecolor='blue', label='P1')
        plt.errorbar(a[2], a[7], yerr=a[8], fmt='ro-', ecolor='red', label='P2')
        plt.errorbar(a[2], a[9], fmt='kx', label='Plin')
        plt.legend(loc=3)
        plt.title('Polarization analysis ' + self._output, fontsize=10)
        plt.ylabel('Stokes parameters')
        plt.xlabel('Angle of linear polarization (degrees)')
        outputfilename = self._output + '_polarizationAnalysis.pdf'
        with PdfPages(outputfilename) as pdf:
            for i in range(1, ifig+2):
                pdf.savefig(plt.figure(i))
        plt.close("all")

    def check(self, data):
        pass

    def clearPreviousData(self, data):
        data.clearCurrent(self._output)

    def fitfunc(self, x, a0, a1, a2):
        return (a0/2.) * (1. + (cos(self.tthana * pi/180.))**2 + ((sin(self.tthana * pi/180.))**2) * (a1*np.cos(2 * (x) * pi/180.) + a2 * np.sin(2 * (x) * pi/180.)))

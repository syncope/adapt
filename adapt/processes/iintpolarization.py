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
from math import pi, cos, sin

from adapt.iProcess import *



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
        self._fit = self._fitNamePar.get()
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
        self._storage["scannumber"].append( int(data.getData("scannumber")) )
        self._storage["peta"].append( data.getData(self._rawdata).getCustomVar('peta') )
        self._storage["ptth"].append( data.getData(self._rawdata).getCustomVar('ptth') )
        self._storage["pr1chi"].append( data.getData(self._rawdata).getCustomVar('pr1chi') )
        self._storage["pr2chi"].append( data.getData(self._rawdata).getCustomVar('pr2chi') )
        self._storage["trapint"].append( data.getData(self._trapint) )
        self._storage["trapint_stderr"].append( data.getData(self._trapint + "_stderr") )
        fitresult = (data.getData(self._fitresult)).best_fit
        self._storage["gaussint"].append( fitresult['m0_amplitude'] )
        self._storage["gaussint_stderr"].append( fitresult['m0_amplitude_stderr'] )

        #~ eta = poldata["peta"][(index-1)*length:index*length]
        #~ iint = poldata["trapezoidIntegral"][(index-1)*length:index*length]
        #~ iinterr = poldata["trapezoidIntegral_stderr"][(index-1)*length:index*length]
        #~ iintgauss = poldata["m0_amplitude"][(index-1)*length:index*length]
        #~ iintgausserr = poldata["m0_amplitude_stderr"][(index-1)*length:index*length]
        #~ pr2chi = np.mean(poldata["pr2chi"][(index-1)*length:index*length])
        #~ pr1chi = np.mean(poldata["pr1chi"][(index-1)*length:index*length])
        #~ polangle = 2*pr2chi
        pass
    
    def finalize(self, data):
        pass
        
        # the name of the input file
        infile = self._inputPar.get()
        
            # first obtain the layout of the file by parsing the header
        with open(infile) as f:
            first_line = f.readline()
            # - remove the leading hash
            line = first_line.split('# ')[1]
            headers = [i for i in line.split('\t')]
            # - remove the trailing newline
            headers.remove('\n')
        # parse the data file
        rawdata = np.loadtxt(infile, unpack=True)
        
        # and finally: build the associative data block
        poldata = { headers[i]: rawdata[i] for i in range(len(headers)) }

        pr1chiana = np.unique(poldata[self._pr1chiNamePar.get()])
        pr2chiana = np.unique(poldata[self._pr2chiNamePar.get()])
        petaana = np.unique(poldata[self._petaNamePar.get()])

        tthana = np.mean(poldata[self._ptthNamePar.get()])


    def check(self, data):
        pass

    def clearPreviousData(self, data):
        data.clearCurrent(self._output)

    def fitfunc(self, x, a0, a1, a2):
        return (a0/2.)*( 1. + ( cos(self.tthana*pi/180.) )**2 + ( (sin(self.tthana*pi/180.))**2 ) * ( a1*np.cos(2*(x)*pi/180.) + a2*np.sin(2*(x)*pi/180.) ))


#~ # polana script
#~ 
#~ import numpy as np
#~ from scipy.optimize import curve_fit
#~ from math import pi, cos, sin, sqrt
#~ 
#~ import matplotlib.pyplot as plt
#~ from matplotlib.backends.backend_pdf import PdfPages
#~ 
#~ infile = "test.iint"
#~ 
#~ fig_size = plt.rcParams["figure.figsize"]
#~ fig_size[0] = 16
#~ fig_size[1] = 12
#~ plt.rcParams["figure.figsize"] = fig_size
#~ 
#~ # first obtain the layout of the file by parsing the header
#~ with open(infile) as f:
    #~ first_line = f.readline()
    #~ # - remove the leading hash
    #~ line = first_line.split('# ')[1]
    #~ headers = [i for i in line.split('\t')]
    #~ # - remove the trailing newline
    #~ headers.remove('\n')
#~ # parse the data file
#~ rawdata = np.loadtxt(infile, unpack=True)
#~ 
#~ # and finally: build the associative data block
#~ poldata = { headers[i]: rawdata[i] for i in range(len(headers)) }
#~ 
#~ pr1chiana = np.unique(poldata["pr1chi"])
#~ pr2chiana = np.unique(poldata["pr2chi"])
#~ petaana = np.unique(poldata["peta"])
#~ 
#~ tthana = np.mean(poldata["ptth"])
#~ 
#~ if len(petaana)*len(pr1chiana) != len(poldata["scannumber"]):
    #~ print("all hell breaks loose")
#~ 
#~ 
#~ 
#~ def fitfunc(x, a0, a1, a2):
    #~ return (a0/2.)*( 1. + ( cos(tthana*pi/180.) )**2 + ( (sin(tthana*pi/180.))**2 ) * ( a1*np.cos(2*(x)*pi/180.) + a2*np.sin(2*(x)*pi/180.) ))
#~ 
#~ 
#~ def someInit(index):
    #~ length = len(petaana)
    #~ eta = poldata["peta"][(index-1)*length:index*length]
    #~ iint = poldata["trapezoidIntegral"][(index-1)*length:index*length]
    #~ iinterr = poldata["trapezoidIntegral_stderr"][(index-1)*length:index*length]
    #~ iintgauss = poldata["m0_amplitude"][(index-1)*length:index*length]
    #~ iintgausserr = poldata["m0_amplitude_stderr"][(index-1)*length:index*length]
    #~ pr2chi = np.mean(poldata["pr2chi"][(index-1)*length:index*length])
    #~ pr1chi = np.mean(poldata["pr1chi"][(index-1)*length:index*length])
    #~ polangle = 2*pr2chi
    #~ return eta, iint, iinterr, iintgauss, iintgausserr, pr1chi, pr2chi, polangle
#~ 
#~ 
#~ # the name of the input file
#~ 
#~ i=1
#~ ifig=1
#~ eta, iint, iinterr, iintgauss, iintgausserr, pr1chi, pr2chi, polangle = someInit(i)
#~ print("eta is : " + str(eta))
#~ print("iint is : " + str(iint))
#~ popt, pcov = curve_fit(fitfunc, eta, iint)
#~ popt, pcov = curve_fit(fitfunc, eta, iint)
#~ 
#~ results = []
#~ 
#~ for i in range(len(pr1chiana)):
    #~ j = i + 1
    #~ eta, iint, iinterr, iintgauss, iintgausserr, pr1chi, pr2chi, polangle = someInit(j)
    #~ for k in range(10):
        #~ popt, pcov = curve_fit(fitfunc, eta, iint, p0=[popt[0],popt[1],popt[2]])
#~ 
    #~ fitresults=[pr1chi, pr2chi, polangle, popt[0], pcov[0,0]**0.5, popt[1], pcov[1,1]**0.5, popt[2], pcov[2,2]**0.5, sqrt(popt[1]**2+popt[2]**2)]
    #~ print(fitresults)
#~ 
    #~ results.append(fitresults)
    #~ 
    #~ if i % 9 == 0:
        #~ ifig=ifig+1
        #~ isubpl=1	
        #~ plt.figure(ifig)
    #~ fig=plt.figure(ifig)
    #~ fig.suptitle('polarization analysis', fontsize=14, fontweight='bold')
    #~ plt.subplot(3,3,isubpl)
    #~ plt.errorbar(eta, iint, yerr=iinterr, fmt='ro', capsize=0, ls='none', color='blue', elinewidth=2, ecolor='black', label='iintsum')
    #~ plt.errorbar(eta, iintgauss, yerr=iintgausserr, fmt='r+', capsize=0, ls='none', color='blue', elinewidth=2, ecolor='black', label='iintgauss')
    #~ xfine = np.linspace(np.amin(petaana), np.amax(petaana), 100)  # define values to plot the function for
    #~ plt.plot(xfine, fitfunc(xfine, *popt), 'r-', label='fit')
    #~ plt.title('Scans #S'+str(int(poldata["scannumber"][(j-1)*len(petaana)]))+'_S'+str(int(poldata["scannumber"][j*len(petaana)-1]))+'\n'+' pr1chi = '+str(int(pr1chi))+'; pr2chi = '+str(int(pr2chi)),fontsize=9)
    #~ plt.legend(fontsize=9, loc=3)
    #~ isubpl=isubpl+1
#~ 
#~ b = np.vstack(results)
#~ 
#~ for i in range(1,ifig+1,1):
    #~ plt.figure(i)
#~ 
#~ #plt.figure(1)
#~ output="testpola"+'.stokes'
#~ np.savetxt(output, b, fmt='%14.4f')
#~ 
#~ 
#~ fig_size[0] = 12
#~ fig_size[1] = 9
#~ plt.rcParams["figure.figsize"] = fig_size
#~ 
#~ a = np.transpose(results)
#~ plt.figure(ifig+1)
#~ plt.errorbar(a[2], a[5], yerr=a[6], fmt='bo-', ecolor='blue',label='P1')
#~ plt.errorbar(a[2], a[7], yerr=a[8], fmt='ro-', ecolor='red',label='P2')
#~ plt.errorbar(a[2], a[9], fmt='kx', label='Plin')
#~ plt.legend(loc=3)
#~ plt.title('Polarization analysis '+str("bla")+'_2.pdf', fontsize=10)
#~ plt.ylabel('Stokes parameters')
#~ plt.xlabel('Angle of linear polarization (degrees)')
#~ output="testblabla"+'_2.pdf'
#~ with PdfPages(output) as pdf:
    #~ for i in range(1,ifig+2):
        #~ pdf.savefig(plt.figure(i))
#~ print("Fits plotted in :"+str(output))
#~ plt.close("all")
#~ 
#~ 


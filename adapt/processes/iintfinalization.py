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

# minimal template example

from adapt import iProcess

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


class iintfinalizationdef(iProcess.IProcessDefinition):

    def __init__(self):
        super(iintfinalizationdef, self).__init__()
        self._ptype = "iintfinalization"
        self.createParameter("outputcolumnnames", "STRINGLIST")
        self.createParameter("outputcolumnlist", "STRINGLIST")
        self.createParameter("outputfilename", "STRING")
        self.createParameter("pdffilename", "STRING")

class iintfinalization(iProcess.IProcess):

    def __init__(self, procDef):
        super(iintfinalization, self).__init__(procDef)
        self._header = self._parameters["outputcolumnnames"]
        self._names = self._parameters["outputcolumnlist"]
        self._outfilename = self._parameters["outputfilename"]
        self._pdfoutfilename = self._parameters["pdffilename"]

    def initialize(self, data):
        self._pdfoutfile = PdfPages(self._pdfoutfilename + ".pdf")


    def execute(self, data):
        # plotting
        #~ plt.plot(motor, observable,         'bo')
        #~ plt.plot(motor, result.best_fit, 'r-')
        #~ self._pdfoutfile.savefig()
        #~ plt.close()

    def finalize(self, data):
        self._pdfoutfile.close()

    def check(self, data):
        pass

#~ 
	#~ if str(fittingfunction) == 'twogaussian' or str(fittingfunction) == 'twolorentzian' or str(fittingfunction) == 'twogaussianfixedcen':
		#~ result = gmod.fit(iintnorm_bckgcorr, x=motor, area=float(parini[0]), cen=float(parini[1]), wid=float(parini[2]),area1=float(parini[3]), cen1=float(parini[4]), wid1=float(parini[5]))
		#~ print(result.fit_report())
		#~ param11=float(result.params['area'].value)
		#~ param12=float(result.params['area'].stderr)	
		#~ param21=float(result.params['cen'].value)
		#~ param22=float(result.params['cen'].stderr)	
		#~ param31=float(result.params['wid'].value)
		#~ param32=float(result.params['wid'].stderr)
		#~ param41=float(result.params['area1'].value)
		#~ param42=float(result.params['area1'].stderr)	
		#~ param51=float(result.params['cen1'].value)
		#~ param52=float(result.params['cen1'].stderr)	
		#~ param61=float(result.params['wid1'].value)
		#~ param62=float(result.params['wid1'].stderr)
		#~ fitresults=[scan_start, track1, track1err, track2, track2err, track3, track3err, pr1chi_value, pr2chi_value, ptth_value, peta_value, integral, integral_stderr, param11, param12, param21, param22, param31, param32, param41, param42, param51, param52, param61, param62]
		
        
fitresults // for double peak fit functions
            =[ scan_start # scan number
            track1, 
            track1err, 
            track2, 
            track2err, 
            track3, 
            track3err, 
            pr1chi_value, 
            pr2chi_value, 
            ptth_value, 
            peta_value, 
            integral, 
            integral_stderr, 
            param11, 
            param12, 
            param21, 
            param22, 
            param31, 
            param32, 
            param41, 
            param42, 
            param51, 
            param52, 
            param61, 
            param62]

/// single peaks
fitresults= [scan_start  # scan number
 track1 # mean val of first "monitored" column
 track1err # error of -> std. dev of first column
 track2 # mean val of second "monitored" column
 track2err # error of -> std. dev of second column
 track3 # mean val of third "monitored" column
 track3err # error of -> std. dev of third column
 pr1chi_value # no idea yet
 pr2chi_value # no idea yet
 ptth_value # no idea yet 
 peta_value # no idea yet
 integral # trapezoid integral val
 integral_stderr # trapezoid integral difference to spline fit
 param11 # area of first fit function
 param12 # std err of above
 param21 # central val of fit function
 param22 # and its std err
 param31 # width of fit function
 param32] # and its std. error

# several steps: 
# final command:
#~ np.savetxt(output, b[1:imax+1], fmt='%14.4f')
# where:
    #~ output=filename_out+'.iint' \\ it's the file name

    #~ b = np.row_stack( (myarray,fitresultsarray) ) \\ myarray and fitsresultsarray are (at least) 2d arrays 
    # where:
    		#~ fitresultsarray=np.asarray(fitresults) \\ see values from above


example:
scan_nr   mean1stcol   stderr1.c      mean2ndcol     stderr2.c      mean3rdcol     stderr3.col
699.0000  100.0810     0.1277         3.9622         0.0057         2.4989         0.0078        
    pr1chi_val      pr2chi_value  ptth_value      peta_value
    90.0000         0.0000        92.1517         0.0000      7391.8494         0.2909      7209.3458       170.7618        45.3166         0.0020         0.0730         0.0020


#~ d = np.loadtxt(output, skiprows=0, unpack=True)

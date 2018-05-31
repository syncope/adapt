# Copyright (C) 2017-8  Christoph Rosemann, DESY, Notkestr. 85, D-22607 Hamburg
# email contact: christoph.rosemann@desy.de
#
# adapt is a programmable data processing toolkit
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

from PyQt4 import QtCore, QtGui, uic
import pyqtgraph as pg


class iintMultiTrackedDataView(pg.GraphicsLayoutWidget):

    def __init__(self, trackinfo, parent = None):
        super(iintMultiTrackedDataView, self).__init__(parent)

        # check the number of plots
        trackedDataValues = trackinfo.value
        trackedDataErrors = trackinfo.error
        resultNames = trackinfo.names
        plotnumber = len(resultNames)

        # divide the plotWidget - decision table how many plots per row
        plotsPerRow = 0
        if plotnumber < 4:
            plotsPerRow = 1
        elif plotnumber <= 6:
            plotsPerRow = 2
        elif plotnumber <= 12:
            plotsPerRow = 3
        elif plotnumber <= 20:
            plotsPerRow = 4
        else:
            plotsPerRow = 5

        self.setWindowTitle(trackinfo.name)

        plotcounter = 0
        for paramname in resultNames:
            p = self.addPlot(title=paramname, x=trackedDataValues, y=trackinfo.getValues(paramname), pen=None, symbolPen=None, symbolSize=10, symbolBrush=(255, 255, 255, 100))
            plotcounter += 1
            if ( plotcounter % plotsPerRow ) == 0:
                self.nextRow()
                plotcounter = 0
        self.show()


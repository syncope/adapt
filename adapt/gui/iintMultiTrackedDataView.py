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
import numpy as np

class iintMultiTrackedDataView(pg.GraphicsLayoutWidget):

    pickedTrackedDataPoint = QtCore.pyqtSignal(str, str, float, float)

    def __init__(self, trackinfo, blacklist=[], parent = None):
        super(iintMultiTrackedDataView, self).__init__(parent)

        # check the number of plots
        trackedDataValues = np.array(trackinfo.value)
        trackedDataErrors = np.array(trackinfo.error)
        
        # remove elements from list by creating and applying a mask
        if blacklist != []:
            blackmask = np.ones(len(trackedDataValues), dtype=bool)
            blackindices = np.array(blacklist)
            blackmask[blackindices] = False
            trackedDataValues = trackedDataValues[blackmask]
            trackedDataErrors = trackedDataErrors[blackmask]
        resultNames = trackinfo.names
        plotnumber = len(resultNames)
        self.scene().sigMouseClicked.connect(self._mouseclick)
        
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
        self.title = trackinfo.name
        self.setWindowTitle(self.title)

        plotcounter = 0
        self._plots = {}
        for paramname in resultNames:
            yvalues = np.array(trackinfo.getValues(paramname))
            if blacklist != []:
                yvalues = yvalues[blackmask]
            self._plots[paramname] = self.addPlot(title=paramname, x=trackedDataValues, y=yvalues, pen=None, symbolPen=None, symbolSize=10, symbolBrush=(255, 255, 255, 100))
            plotcounter += 1
            if ( plotcounter % plotsPerRow ) == 0:
                self.nextRow()
                plotcounter = 0
        self.show()

    def _mouseclick(self, ev):
        # check whether a point on a plot has been clicked
        # at second click the connection is activated
        # effectively this means: double-click will call the appropriate function
        if isinstance(ev.currentItem, pg.graphicsItems.ScatterPlotItem.ScatterPlotItem):
            ci = ev.currentItem
            ci.sigClicked.connect(self._spotIt)

    def _spotIt(self, spi, si):
        # called from the mouseClick event after the point has been connected
        for plot in self._plots.items():
            if spi in plot[1].vb.allChildren():
                paramname = plot[0]
        # point position:
        position= si[0].pos()
        self.pickedTrackedDataPoint.emit(self.title, paramname, position.x(), position.y())

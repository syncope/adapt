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


class XYZdef(iProcess.IProcessDefinition):

    def __init__(self):
        super(XYZdef, self).__init__()
        self._ptype = "XYZ"
        #~ self.createParameter("@@@@@@@", "STRING")
        #~ self.createParameter("@@@@@@@", "INT")
        #~ self.createParameter("@@@@@@@", "FLOAT")
        #~ self.createParameter("@@@@@@@", "BOOL")
        #~ self.createParameter("@@@@@@@", "STRINGLIST")
        #~ self.createParameter("@@@@@@@", "INTLIST")
        #~ self.createParameter("@@@@@@@", "FLOATLIST")
        #~ self.createParameter("@@@@@@@", "BOOLLIST")
        #~ self.createParameter("@@@@@@@", "STRING", optional=True)

class XYZ(iProcess.IProcess):

    def __init__(self, procDef):
        super(XYZ, self).__init__(procDef)

    def initialize(self):
        pass

    def execute(self, data):
        pass

    def finalize(self, data):
        pass

    def check(self, data):
        pass

    def clearPreviousData(self, data):
        pass

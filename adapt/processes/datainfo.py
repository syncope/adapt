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

# minimalistic: print out data info after each iteration

from adapt import iProcess


class datainfodef(iProcess.IProcessDefinition):

    def __init__(self):
        super(datainfodef, self).__init__()
        self._ptype = "datainfo"

class datainfo(iProcess.IProcess):

    def __init__(self, procDef):
        super(datainfo, self).__init__(procDef)

    def initialize(self, data):
        pass

    def execute(self, data):
        data.info()

    def finalize(self, data):
        print("At the end of the run, the data info is:")
        data.info()

    def check(self, data):
        pass

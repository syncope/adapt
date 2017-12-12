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

# a builder that can creates processes from their definition/parameters


from . import processes


class ProcessBuilder():

    def __init__(self):
        pass

    def createProcessFromDefinition(self, procdef):
        try:
            processType = procdef.getProcessType()
        except:
            print("[ProcessBuilder] Cannot build the specified type of process for: \n" + str(procdef))
        return getattr(getattr(processes, processType), processType)(procdef)

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

# rewritten...
# this class accepts a processing configuration
#  -- a list of strings that present the order of execution of processes
#  -- a dictionary of processDefinitions with the name (string) as key

# it returns a processList -- which then can be run by an execution model


from . import processingConfiguration
from . import processFactory


class ProcessListBuilder():

    def createProcessList(self, procConf):
        self._procConf = procConf
        pDefs = self._procConf.getProcessDefinitions()

        executionList = []
        for pname in self._procConf.getOrderOfExecution():
            executionList.append(
                processFactory.ProcessFactory(
                ).createProcessFromDefinition(
                    pDefs[
                        pname]))
        return executionList

if __name__ == "__main__":
    from . import configParserFileAccess
    processingConfig = configParserFileAccess.ConfigParserFileAccess().read(
        "test.ini")
    plb = ProcessListBuilder()
    pList = plb.createProcessList(processingConfig)
    print(" created a process list that can be executed: ")
    print(repr(pList))

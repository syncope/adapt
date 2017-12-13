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

# this is the abstract definition of the persistency of configuration
# currently only one method is foreseen, but maybe this wil change

import yaml

import iConfigurationHandler
import processingConfiguration


class ConfigurationHandler(iConfigurationHandler.IConfigurationHandler):

    def __init__(self):
        self._datablob = None
        self._procConfig = processingConfiguration.ProcessingConfiguration()

    def loadConfig(self, filename):
        with open(filename) as blob:
            self._datablob = yaml.load(blob)
        self._serialize()
        return self._procConfig

    def writeConfig(self, filename, procconf):
        dumpDict = {}
        dumpDict["execlist"] = procconf.getOrderOfExecution()
        for k,v in procconf.getProcessDefinitions().items:
            dumpDict[k] = v
        
        with open(filename, 'w') as outfile:
            yaml.dump(dumpDict, outfile, default_flow_style=False)

    def _serialize(self):
        try:
            self._procConfig.setOrderOfExecution(self._datablob["execlist"])
        except KeyError("No [execlist] item in config. Exiting."):
            exit()
        try:
            for procname in self._execList:
                self._procConfig.addSingleProcessDefinition(procname, self._datablob[procname])
        except KeyError("Item in execlist has no corresponding entry."):
            exit()

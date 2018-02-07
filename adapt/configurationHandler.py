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

from . import iConfigurationHandler
from . import processingConfiguration


class ConfigurationHandler(iConfigurationHandler.IConfigurationHandler):
    '''An actual implementation of a configuration handler.
       The file persistency is performed with using YAML.'''

    def __init__(self):
        '''Constructs with an empty config file.
           Uses composition with a processing configuration object inside.'''
        self._datablob = None
        self._procConfig = processingConfiguration.ProcessingConfiguration()

    def loadConfig(self, filename):
        '''Loads a yaml file and returns the processingConfiguration.
           :param filename: the filename of the configuration file
           :type filename: a yaml configuration file'''
        with open(filename) as blob:
            self._datablob = yaml.load(blob)
        self._serialize()
        return self._procConfig

    def writeConfig(self, filename, procconf):
        '''Writes the given processing configuration to a yaml file.
           :param filename: The name of the yaml file to be created
           :param procconf: The processing configuration object'''
        dumpDict = {}
        dumpDict["execlist"] = procconf.getOrderOfExecution()
        for k,v in procconf.getProcessDefinitions().items:
            dumpDict[k] = v
        with open(filename, 'w') as outfile:
            yaml.dump(dumpDict, outfile, default_flow_style=False)

    def _serialize(self):
        try:
            execlist = self._datablob["execlist"]
            self._procConfig.setOrderOfExecution(execlist)
        except KeyError("No [execlist] item in config. Exiting."):
            exit()
        try:
            for procname in execlist:
                self._procConfig.addSingleProcessDefinition(procname, self._datablob[procname])
        except KeyError("Item in execlist has no corresponding entry."):
            exit()

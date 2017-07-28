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

# this is the actual implementation of config file persistency
# it is based on the built-in config file parser of python3

from __future__ import absolute_import

from configparser import ConfigParser

from . import utilities
from . import iConfigFileAccess
from . import processingConfiguration
from . import processDefinitionFactory


class ConfigParserFileAccess(iConfigFileAccess.IConfigFileAccess):

    def __init__(self):
        # the parser has little changes wrt the original
        # why composition instead of inheritance? -> i want to hide it
        self.parser = ConfigParser(
            default_section="global_override_section",
            strict=True,
            delimiters=('='),
            comment_prefixes=('#'),
            inline_comment_prefixes=('#'))
        self.parser.optionxform = lambda option: option

    def read(self, filename):
        '''reads from the given file'''
        executionList, procDefDict = self._parse(filename)
        self._createProcessDefsFromDict(procDefDict)

        return processingConfiguration.ProcessingConfiguration(
            executionList, procDefDict)

    def _parse(self, filename):
        # parse the file -> allows to access the sections, etc.
        self.parser.read(filename)

        # create a map of maps/dict of dicts:
        # [ sectionname: [ sectiondictionary] ]
        dictOfSectionDicts = {}
        try:
            executionOrder = utilities.castValueToType(
                self.parser["processlist"]["execute"],
                "STRINGLIST")
        except KeyError:
            print(' The [processlist] entry MUST exist, is it missing? ')
            exit()
        # now iterate over the sections; section is the given name
        for section in self.parser.sections():
            # skip the steering part
            if(section == "processlist"):
                continue
            # create temporary dictionary for storing
            sectionDict = {}
            for (key, value) in self.parser[section].items():
                sectionDict[key] = value
            dictOfSectionDicts[section] = sectionDict

        return executionOrder, dictOfSectionDicts

    def _createProcessDefsFromDict(self, pDD):
        '''Private function that creates the process definitions
           specifically from a dictionary.'''
        defFactory = processDefinitionFactory.ProcessDefinitionFactory()

        for name in pDD:
            pDD[name] = defFactory.createProcessDefinitionFromDict(pDD[name])

    def write(self, filename, config):
        ''' writes the given config to the file as specified'''
        pass


if __name__ == "__main__":
    cpfa = ConfigParserFileAccess()
    processingConfig = cpfa.read("test.ini")
    steercfg = processingConfig.getOrderOfExecution()
    procDefs = processingConfig.getProcessDefinitions()
    print("exec: " + repr(steercfg))

    for name in procDefs:
        print("process name is : " + name)
        for p in procDefs[name].getParameters():
            print(" parameter name:: " + p + " with value: "
                  + repr(procDefs[name].getParameter(p).getValue()))

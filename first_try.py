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

# this is just a first tryout to string the pieces together

# see if it will work


def parseConfig(filename):
    try:
        import core.configFileParser as cfgparser
    except:
        print("ConfigFileParser not found. Exiting.")
        exit()

    parser = cfgparser.ConfigFileParser()
    return parser.readConfigObjects(filename)


def createProcesses(cfgObjDict):
    try:
        import core.processListBuilder as processbuilder
    except:
        print("ProcessListBuilder not found. Exiting.")
        exit()

    builder = processbuilder.ProcessListBuilder()
    return builder.buildProcessList(cfgObjDict)


def executeSerially(orderedProcessList, procData):
    try:
        import core.serialExecutor as serialexecute
    except:
        print("SerialExecutor not found. Exiting.")
        exit()

    executor = serialexecute.SerialExecutor(procData)

    executor.setProcesses(orderedProcessList)
    executor.runInitialization()
    executor.runLoop()
    executor.runFinalization()


if __name__ == "__main__":
    a = parseConfig("test.ini")
#    a = parseConfig("longtest.ini")

    b, c = createProcesses(a)
    executeSerially(b,c)

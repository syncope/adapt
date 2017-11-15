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
        from adapt import configParserFileAccess as cfgparser
    except ImportError("ConfigFileParser not found. Exiting."):
        exit()

    parser = cfgparser.ConfigParserFileAccess()
    return parser.read(filename)


def createProcesses(cfgObjDict):
    try:
        from  adapt import processListBuilder as processbuilder
    except:
        print("ProcessListBuilder not found. Exiting.")
        exit()

    builder = processbuilder.ProcessListBuilder()
    return builder.createProcessList(cfgObjDict)


def executeSerially(orderedProcessList):
    try:
        import adapt.serialExecutor as serialexecute
    except:
        print("SerialExecutor not found. Exiting.")
        exit()

    executor = serialexecute.SerialExecutor()

    executor.run(orderedProcessList)


if __name__ == "__main__":
    #~ a = parseConfig("adapt/test.ini")
    a = parseConfig("adapt/test2.ini")
#    a = parseConfig("longtest.ini")

    b = createProcesses(a)
    executeSerially(b)

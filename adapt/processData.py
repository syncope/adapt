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


class ProcessData():

    '''This class acts a shared data source and sink between processes.
       It implements a publish - subscribe like pattern.
       Two separate entities are kept; a global and unchangeable part,
       and a part which can be cleared by a command call.
       It's polymorphic, access is handled by name.'''

    def __init__(self):
        self.globaldata = {}
        self.currentdata = {}

    def clearCurrent(self, name=None):
        import collections
        if isinstance(name, list):
            for n in name:
                self.clearCurrent(n)
        else:
            if name is None:
                self.currentdata.clear()
            else:
                try:
                    del self.currentdata[name]
                except:
                    pass

    def clearAll(self):
        self.currentdata.clear()
        self.globaldata.clear()

    def addData(self, name, data):
        if name in self.currentdata:
            raise RuntimeError("[ProcessData] Error: A process tried to"
                               + " overwrite existing data of name " + str(name) + "!")
        else:
            self.currentdata[name] = data

    def addGlobalData(self, name, data):
        if name in self.globaldata:
            raise RuntimeError("Error: a process tried to"
                               + " overwrite global data of name " + str(name) + "!")
        else:
            self.globaldata[name] = data

    def getData(self, name):
        try:
            return self.globaldata[name]
        except:
            return self.currentdata[name]

    def info(self):
        for gdk, gdv in self.globaldata.items():
            print("[info] global data with key: "
                  + repr(gdk) + " and value: " + repr(gdv))
        for cdk, cdv in self.currentdata.items():
            print("[info] current data with key: "
                  + repr(cdk) + " and value: " + repr(cdv))

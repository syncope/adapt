# Copyright (C) 2017-8  Christoph Rosemann, DESY, Notkestr. 85, D-22607 Hamburg
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

# a class to create an abstract definition of a process parameter


class ProcessParameter():
    '''An object to hold all information needed for parameters.'''

    def __init__(self, name=None, partype=None, defval=None, optional=False):
        self.name = name
        self._type = partype
        self.value = defval
        self.optional = optional

    def typecheck(self, val):
        if type(val) is self._type:
            return True
        else:
            return False

    def set(self, val):
        if self.typecheck(val):
            self.value = val
        else:
            raise ValueError("Can't set parameter " + str(self.name) + " because it's of the wrong data type.")

    def get(self):
        return self.value

    def isOptional(self):
        return self.optional

    def dump(self):
        return (self.name, self._type, self.value, self.optional)


class ProcessParameters(dict):

    def __init__(self, *arg, **kw):
        super(ProcessParameters, self).__init__(*arg, **kw)

    def add(self, pp: ProcessParameter):
        self[pp.name] = pp

    def setValue(self, name, value):
        try:
            self[name] = value
        except KeyError:
            raise KeyError("In the dictionary of the process parameters there is no entry with the name " + str(name) + " . Please check.")

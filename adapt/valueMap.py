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

# a simple representation of a map -- a dictionary
# exchange object for persistency


class ValueMap():
    '''A simple exchange object, basically a dictionary'''

    def __init__(self):
        self._map = {}

    def add(self, key, val):
        self._map[key] = val

    def get(self, key):
        try:
            return self._map[key]
        except KeyError("[ValueMap] Cannot retrieve value for invalid key " + str(key) + "."):
            exit()

    def numberOfElements(self):
        return len(self._map)

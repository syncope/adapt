# Copyright (C) 2016-17  Christoph Rosemann, DESY, Notkestr. 85, D-22607 Hamburg
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


class IConfigurationHandler():
    '''Abstract definition of what a handler of configuration should be able to do.
       This provides an interface to the persistency of config files:
        - loadConfig: loads a valid config file
        - writeConfig: writes a valid config file'''

    def loadConfig(self, filename):
        pass

    def writeConfig(self, filename, config):
        pass

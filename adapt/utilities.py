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

# this is loose array of helper functions and classes


def castValueToType(pValue, pType):
    '''This is a helper function that casts a config value to the defined type.
       It takes two arguments, the value of the config file, as parsed;
       and the data type as defined in the process constructor.'''
    def prepareForList(tempList):
        t = tempList.replace('[', '')
        t = t.replace('\n','')
        t = t.replace(']', '')
        t = t.replace(' ', '')
        return t.split(',')
    try:
        if pType == "INT":
            return int(pValue)
        elif pType == "FLOAT":
            return float(pValue)
        elif pType == "BOOL":
            return bool(pValue)
        elif pType == "STRING":
            return str(pValue)
        elif pType == "INTLIST":
            tempList = prepareForList(pValue)
            for i in tempList:
                i = int(i)
            return tempList
        elif pType == "FLOATLIST":
            tempList = prepareForList(pValue)
            for i in tempList:
                i = float(i)
            return tempList
        elif pType == "BOOLLIST":
            tempList = prepareForList(pValue)
            for i in tempList:
                i = bool(i)
            return tempList
        elif pType == "STRINGLIST":
            tempList = prepareForList(pValue)
            for i in tempList:
                i = str(i)
            return tempList
    except:
        raise Exception("Casting " + repr(pValue)
                        + " to type " + repr(pType) + " failed.")


if __name__ == "__main__":
    print("try: " + str(castValueToType(3.14, "FLOAT")))

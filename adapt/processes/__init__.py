# Copyright (C) 2017-19  Christoph Rosemann, DESY, Notkestr. 85, D-22607 Hamburg
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

from . import globaldata
from . import datainfo
from . import stdreader
from . import specfilereader
from . import polarintegration
from . import sliceprojection
from . import iintdefinition
from . import iintfinalization
from . import iintpolarization
from . import iintcontrolplots
from . import iintscanprofileplot
from . import iintmcaplot
from . import iintscanplot
from . import filter1d
from . import subsequenceselection
from . import backgroundsubtraction
from . import curvefitting
from . import trapezoidintegration
from . import gendatafromfunction
from . import integratefitresult

processTypeList = ["globaldata",
                   "datainfo",
                   "stdreader",
                   "specfilereader",
                   "polarintegration",
                   "sliceprojection",
                   "iintdefinition",
                   "iintfinalization",
                   "iintpolarization",
                   "iintcontrolplots",
                   "iintscanprofileplot",
                   "iintmcaplot",
                   "iintscanplot",
                   "filter1d",
                   "subsequenceselection",
                   "backgroundsubtraction",
                   "curvefitting",
                   "trapezoidintegration",
                   "gendatafromfunction",
                   "integratefitresult"
                   ]

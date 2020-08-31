# Copyright (C) 2017-20  Christoph Rosemann, DESY, Notkestr. 85, D-22607 Hamburg
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

# simple implementation of a line cut, P03 style

from adapt.iProcess import *

import numpy
from numpy import sin, cos, arctan, degrees, radians, pi, ceil, floor, sqrt

class processname(IProcess):

    def __init__(self, ptype="processname"):
        super(processname, self).__init__(ptype)

        #~ self._xxxPar = ProcessParameter("someName", someType)
        #~ self._parameters.add(self._xxxPar)

    def initialize(self):
        #~ self._xxx = self._xxxPar.get()
        pass

    def execute(self, data):
        #~ datum = data.getData(arg)
        pass

    def finalize(self, data):
        pass

    def check(self, data):
        pass

    def clearPreviousData(self, data):
        pass


import numpy
from numpy import sin, cos, arctan, degrees, radians, pi, ceil, floor, sqrt
from scipy import ndimage
from base import dpdak_image
from base.dpdak import *
import fabio
import os
from os.path import basename

# q_space globals 0-6
# 0 wl: wave length [nm]
# 1 sd: sample detector distance [mm]
# 2 pixel size x and y [um]
# 3 dbx: direct beam x position [pixel]
# 4 dbx: direct beam x position [pixel]
# 5 a_i: incident angle [deg]
# pp: pixel position

def alpha_f(pp_y, db_y, ps_y, sdd, a_i):
    return degrees(arctan((pp_y - db_y) * ps_y / sdd)) - a_i

def ttheta_f(pp_x, db_x, ps_x, sdd):
    return degrees(arctan((pp_x - db_x) * ps_x / sdd))

def q_z(wl, a_f, a_i):
    return (2 * pi / wl) * (sin(radians(a_f)) + sin(radians(a_i)))

def q_parallel(wl, tt_f, a_f, a_i):
    q_y = (2 * pi / wl) * sin(radians(tt_f)) * cos(radians(a_f))
    q_x = (2 * pi / wl) *(cos(radians(tt_f)) * cos(radians(a_f)) - cos(radians(a_i)))
    return ((-1)**(q_y < 0))*sqrt(q_x**2+q_y**2)

class LineIntegrationP03(BasePlugin):
    
    description = {
        NAME      : 'Line Integration P03',
        AUTHOR    : 'Matthias Schwartzkopf & Gunthard Benecke & Jannik Woehnert',
        VERSION   : '2.0',
        IN        : {
            0: {NAME: 'image_path', TYPE: FILE_PATH, UNIT: ''},
            1: {NAME: 'q_space', TYPE: FLOAT_1D, UNIT: ''},
            2: {NAME: 'manipulators (opt.)', TYPE: FLOAT_1D, UNIT: ''}
        },
        OUT       : {
            0: {NAME: 'x-Axis', TYPE: FLOAT_1D, UNIT: ''},
            1: {NAME: 'Intensity', TYPE: FLOAT_1D, UNIT: ''}
        },
        PARAMETER : {
            0: {NAME: 'Cut Direction', TYPE: CHOICE, DEFAULT: 'Horizontal', 
                OPTIONS: ['Horizontal', 'Vertical']},
            1: {NAME: 'x [pixel]', TYPE: INT, DEFAULT: 1},
            2: {NAME: 'y [pixel]', TYPE: INT, DEFAULT: 1},
            3: {NAME: 'width [pixel]', TYPE: INT, DEFAULT: 1},
            4: {NAME: 'height [pixel]', TYPE: INT, DEFAULT: 1},
            5: {NAME: 'x-Axis Unit', TYPE: CHOICE, DEFAULT: 'q [nm^-1]', 
                 OPTIONS: ['q [nm^-1]', 'q [A^-1]', 'angle [deg]', 'pixel']},
            6: {NAME: 'Mirror Cut', TYPE: BOOL, DEFAULT: False}
        }    
    }     
 
    def getData(self, logger, counter, parameter, requires):
        image = dpdak_image.open_image(requires[0])
        manipulator_BOOL = True
        
        if len(image) == 0:
            logger.add_error('no image found')
            return None
        q_space = requires[1]
        if len(q_space) != 8 :
            logger.add_error('no q-space defined')
            return None
        manipulators = requires[2]
        if len(manipulators) != 7 :
            logger.add_error('no manipulator defined. continue without manipulation')
            manipulator_BOOL = False
        
        """ q-space """
        #################################################
        
        cut_dir = parameter[0]
        width, height = parameter[3], parameter[4]
        wl = q_space[0]
        sdd = q_space[1]
        ps_x, ps_y = q_space[2] * 0.001, q_space[2] * 0.001
        a_i = q_space[5]

        #display coordinates start a (1,1)
        x, y = parameter[1] - 1, parameter[2] - 1
        mirror_cut = parameter[6]
        db_x, db_y = q_space[3] - 1, q_space[4] - 1
        
        
        
        """ Image Manipulator """
        #################################################
        if manipulator_BOOL:
            cbfHeader = fabio.open(requires[0]).header
            mask = numpy.zeros(image.shape)
            try:
                """
                Mask should be in fomat
                >0 for detector gap pixel
                else zero
                """
                mask = dpdak_image.open_image(dpdak_image.config.get('mask_image'), LI_neo=True)
                mask[mask != 0] = 1
                assert(mask.shape == image.shape)
            except:
                mask = numpy.zeros(image.shape)
                logger.add_info('no mask defined. Continue without mask.')
                
            binX = manipulators[0]
            binY = manipulators[1]
            sumImage = manipulators[2]
            flip_BOOL = manipulators[3]
            dectX = manipulators[4]
            dectY = manipulators[5]
            safe_BOOL = manipulators[6]
            
            dectBOOL = dectX != 0 or dectY != 0
            
            # create path array for sum images
            path = requires[0].split('.')[-2]
            number = path.split('_')[-1]
            nrLEN = len(number)
            nr = int(number)
            if sumImage == 1 and not dectBOOL:
                myloop = [0]
            myloop = range(sumImage * (1 + dectBOOL))
            path_array = list()
            for i in myloop:
                newnumber = str(i + nr).zfill(nrLEN) + '.'
                path_array.append(requires[0].replace(number + '.', newnumber))
                
            
            # start sum image loop
            newimage = numpy.zeros(image.shape)
            for i, imagePath in enumerate(path_array[::1 + dectBOOL]):
                try:
                    image = dpdak_image.open_image(imagePath, LI_neo=True)
                except:
                    logger.add_error('Line Integration NEO: file ' + imagePath + ' does not exists.')
                    return None
    
                # detector shift
                if not dectBOOL:
                    pass
                else:
                    shift_im = dpdak_image.open_image(path_array[2 * i + 1], LI_neo=True)
                    shifted_image = ndimage.shift(shift_im, [dectY, -dectX], cval=0.0)
                    shifted_mask = ndimage.shift(mask, [dectY, -dectX], cval=0.0)
                    
                    image = (image + shifted_image * mask + shifted_image + image * shifted_mask)
                            
                
                # flip image and add
                if flip_BOOL:
                    flipped_image = numpy.fliplr(image)
                    flipped_mask = numpy.fliplr(mask)
                    pixel_shift = 2 * (newimage.shape[1] / 2. - db_x)
                    flipped_image = ndimage.shift(flipped_image, [0, -pixel_shift], cval=0.0)
                    flipped_mask = ndimage.shift(mask, [0, -pixel_shift], cval=0.0)
                    
                    image = (image + flipped_image * mask + flipped_image + image * flipped_mask)
                                   
                            
                            
                # binning
                image_copy = numpy.copy(image)
                if binX != 0:
                    for j in range(newimage.shape[1]):
                        for l in range(1, 1 + binX):
                            if j + l < newimage.shape[1]:
                                image[:, j] += image_copy[:, j + l]
                            if j - l >= 0:
                                image[:, j] += image_copy[:, j - l]
                if binY != 0:
                    for j in range(newimage.shape[0]):
                        for l in range(1, 1 + binY):
                            if j + l < newimage.shape[0]:
                                image[j, :] += image_copy[j + l, :]
                            if j - l >= 0:
                                image[j, :] += image_copy[j - l, :]
                
                # add manipulated image to sum up images                    
                newimage += image
                
                
            if safe_BOOL:
                try:
                    safe_image = fabio.cbfimage.CbfImage(newimage, cbfHeader)
                    filename = basename(requires[0])
                    
                    if not os.path.exists('LineIntegrationNeo'):
                        os.makedirs('LineIntegrationNeo')
                                          
                    safe_image.write('LineIntegrationNeo/' + filename)
                except:
                    logger.add_info('Safe modified images: Error in IO.')
            
            # rewrite newimage to image
            try:
                image = numpy.ma.masked_array(newimage, mask)   
            except:
                image = newimage
                logger.add_info('Image manipulator modified Image, mask no longer fit. Continue without')
          
        ######################################################
    

        if x < 0 or x >= image.shape[1]:
            logger.add_error('Line Integration: x has to be in range 1-' + 
                             str(image.shape[1]))
            return None
            
        if width < 1 or width > image.shape[1]-x:
            logger.add_error('Line Integration: width has to be in range 1-' + 
                             str(image.shape[1]-x))
            return None
 
        if y < 0 or y >= image.shape[0]:
            logger.add_error('Line Integration: y has to be in range 1-' + 
                             str(image.shape[0]))
            return None

        if height < 1 or height > image.shape[0]-y:
            logger.add_error('Line Integration: height has to be in range 1-' + 
                             str(image.shape[0]-y))
            return None

        if cut_dir == 'Vertical' and mirror_cut:
            if x > db_x and (x - 2*numpy.abs(db_x-x)-width) < 1:
                mirror_cut = False
                logger.add_warning('Line Integration: mirror cut would be out of bond. continue without.')
            if x <= db_x and (x + 2*numpy.abs(db_x-x)) >= image.shape[1]:
                mirror_cut = False
                logger.add_warning('Line Integration: mirror cut would be out of bond. continue without.')
        else:
            mirror_cut = False
            


        axis = 0 if cut_dir == 'Horizontal' else 1
        if mirror_cut == False:
            cut = image[y:y+height,x:x+width].sum(axis=axis)
        else:
            new_x = int(x - 2*numpy.abs(db_x-x)-width) if x>db_x else int(x + 2*numpy.abs(db_x-x)-width)
            cut = (numpy.array(image[y:y+height,new_x:new_x+width].sum(axis=axis))+
                       numpy.array(image[y:y+height,x:x+width].sum(axis=axis)))

        cut =  cut / float(height if cut_dir == 'Horizontal' else width)
        
        if cut_dir == 'Horizontal':
            pixel = x + numpy.arange(width)
            a_f = alpha_f(y + (height / 2.), db_y, ps_y, sdd, a_i)
            tt_f = ttheta_f(pixel, db_x, ps_x, sdd)
            if parameter[5] == 'pixel': x_range = pixel + 1
            elif parameter[5] == 'angle [deg]': x_range = tt_f
            elif parameter[5] == 'q [A^-1]': x_range = q_parallel(wl, tt_f, a_f, a_i) * 10. 
            else: x_range = q_parallel(wl, tt_f, a_f, a_i)
        else:
            pixel = y + numpy.arange(height)
            a_f = alpha_f(pixel, db_y, ps_y, sdd, a_i)            
            if parameter[5] == 'pixel': x_range = pixel + 1
            elif parameter[5] == 'angle [deg]': x_range = a_f
            elif parameter[5] == 'q [A^-1]': x_range = q_z(wl, a_f, a_i) * 10. 
            else: x_range = q_z(wl, a_f, a_i)

        if isinstance(cut, numpy.ma.core.MaskedArray):
            cut[cut.mask] = numpy.nan
            
        
        return {0: x_range, 1: cut}

# define the actual fitfunctions

import numpy as np

import function1d

class gauss(function1d.iFunction1D):
    def __init__(self):
       super(gauss, self).__init__(3)

    def _implementation(self, par, x):
        N = par[0]
        mean = par[1]
        sigma = par[2]
        return N* np.exp( - ((x - mean)/sigma)**2 )


class lorentz(function1d.iFunction1D):
    def __init__(self):
        super(lorentz, self). __init__(3)


    def _implementation(self, par, x):
        amplitude = par[0]
        position = par[1]
        fwhm = par[2]
        return amplitude / (1 + np.power((x - position) / (fwhm * 0.5), 2))


class pseudoVoigt(function1d.iFunction1D):
    def __init__(self):
        super(pseudeVoigt, self). __init__(ASD)


    def _implementation(self, par, x):
        return 1.



if __name__ == "__main__":
    g1 = gauss()
    g2 = gauss()
    g3 = gauss()
    model = function1d.combined1Dfunction(g1)
    model.addFunction(g2)
    print("values at 0: " + str(g1([1.,0.,3.],0.)) + " and " + str(g2([2.,1.,1.],0.)) + " and " + str(g3( [2.,1.,1.], 0.)))
    model([1.,0.,3.,2.,1.,1.], 0.)
    model.multiplyFunction(g3)
    model([1.,0.,3.,2.,1.,1., 2.,1.,1.], 0.)

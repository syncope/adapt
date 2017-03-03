# 1d functions

# abstract function definition
# sets the basic structure and how to add/multiply functions

import numpy as np


class iFunction1D():

    def __init__(self, nop):
        self._nop = nop
        self._param = np.zeros(nop)

    def getNumberOfParameters(self):
        return self._nop

    def __call__(self, par, x):
        try:
            return self._implementation(par, x)
        except IndexError("The number of parameters in the function \
                             doesn't match the given number of \
                             parameters."):
            pass

    def _implementation(self, par, x):
        pass


class combined1Dfunction(iFunction1D):

    def __init__(self, func):
        self._f = [func]
        self._FUNC = "value[0]"
        self._tnop = func.getNumberOfParameters()

    def _updateNumbers(self):
        n = 0
        for f in self._f:
            n += f.getNumberOfParameters()
        self._tnop  = n

    def _implementation(self, par, x):
        value = self._calculateComponents(par, x)
        print(eval(self._FUNC))

    def _calculateComponents(self, par, x):
        paroffset = 0
        results = []
        for f in self._f:
            nop = paroffset + f.getNumberOfParameters()
            results.append( f(par[paroffset:nop],x) )
            paroffset = nop
        return results
        
    def addFunction(self, func):
        self._f.append(func)
        self._updateNumbers()
        self._FUNC = "("  + self._FUNC + " + value[" + str(self._f.index(func)) + "])"

    def multiplyFunction(self, func):
        self._f.append(func)
        self._updateNumbers()
        self._FUNC = "("  + self._FUNC + " * value[" + str(self._f.index(func)) + "])"

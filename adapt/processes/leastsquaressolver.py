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

# this is a first shot at a least square optimizer interface

import scipy.optimize.leastsq as leastsq
import iProcess


class simpleleastsquares(iProcess.IProcess):

    def __init__(self):
        iProcess.IProcess.__init__(self)
        # names of in- and output
        self.defineParameter("input", "STRING", "data")
        self.defineParameter("dataname", "STRING")

        # information about the function
        self.defineParameter("detectorname", "STRING", None)
        self.defineOptionalParameter("custommask", "STRING", None)

        # original pyfai parametrization
        self.defineOptionalParameter("poni1", "FLOAT", None)
        self.defineOptionalParameter("poni2", "FLOAT", None)
        self.defineOptionalParameter("rot1", "FLOAT", 0.)
        self.defineOptionalParameter("rot2", "FLOAT", 0.)
        self.defineOptionalParameter("rot3", "FLOAT", 0.)

        # and old-style fit2d
        self.defineOptionalParameter("fit2dstyle", "BOOL", False)
        self.defineOptionalParameter("center1", "INT", None)
        self.defineOptionalParameter("center1", "INT", None)
        self.defineOptionalParameter("tilt", "FLOAT", 0.)
        self.defineOptionalParameter("tiltrotation", "FLOAT", 0.)

        # now real parameters that steer the integration
        self.defineParameter("nbins", "INT")
        self.defineOptionalParameter("azimlowlim", "FLOAT", None)
        self.defineOptionalParameter("azimhighlim", "FLOAT", None)
        self.defineOptionalParameter("radiallowlim", "FLOAT", None)
        self.defineOptionalParameter("radialhighlim", "FLOAT", None)

    def initialize(self, data):
        self._input = self.getParameterValue("input")
        self._dataname = self.getParameterValue("dataname")
        self._nbins = self.getParameterValue("nbins")
        _detector = self.getParameterValue("detectorname")
        _wavelength = data.getData("wavelength")
        _distance = data.getData("sdd")

    def execute(self, data):
        pass

    def finalize(self, data):
        pass

    def check(self, data):
        pass

if __name__ == "__main__":
    s = simpleleastsquares()
    for p, k in s._parameters.items():
        print(p + " with name " + k._name)


# the currently available version for startes
# scipy.optimize.leastsq(func, x0, args=(), Dfun=None, full_output=0, col_deriv=0, ftol=1.49012e-08, xtol=1.49012e-08, gtol=0.0, maxfev=0, epsfcn=None, factor=100, diag=None)[source]
    #~ func : callable
        #~ should take at least one (possibly length N vector) argument and returns M floating point numbers. It must not return NaNs or fitting might fail.
#~
    #~ x0 : ndarray
        #~ The starting estimate for the minimization.
#~
    #~ args : tuple, optional
        #~ Any extra arguments to func are placed in this tuple.
#~
    #~ Dfun : callable, optional
        #~ A function or method to compute the Jacobian of func with derivatives across the rows. If this is None, the Jacobian will be estimated.
#~
    #~ full_output : bool, optional
        #~ non-zero to return all optional outputs.
#~
    #~ col_deriv : bool, optional
        #~ non-zero to specify that the Jacobian function computes derivatives down the columns (faster, because there is no transpose operation).
#~
    #~ ftol : float, optional
        #~ Relative error desired in the sum of squares.
#~
    #~ xtol : float, optional
        #~ Relative error desired in the approximate solution.
#~
    #~ gtol : float, optional
        #~ Orthogonality desired between the function vector and the columns of the Jacobian.
#~
    #~ maxfev : int, optional
        #~ The maximum number of calls to the function. If Dfun is provided then the default maxfev is 100*(N+1) where N is the number of elements in x0, otherwise the default maxfev is 200*(N+1).
#~
    #~ epsfcn : float, optional
        #~ A variable used in determining a suitable step length for the forward- difference approximation of the Jacobian (for Dfun=None). Normally the actual step length will be sqrt(epsfcn)*x If epsfcn is less than the machine precision, it is assumed that the relative errors are of the order of the machine precision.
#~
    #~ factor : float, optional
        #~ A parameter determining the initial step bound (factor * || diag * x||). Should be in interval (0.1, 100).
#~
    #~ diag : sequence, optional
        #~ N positive entries that serve as a scale factors for the variables.

# Returns:
    #~ x : ndarray
        #~ The solution (or the result of the last iteration for an unsuccessful call).
#~
    #~ cov_x : ndarray
        #~ Uses the fjac and ipvt optional outputs to construct an estimate of the jacobian around the solution. None if a singular matrix encountered (indicates very flat curvature in some direction). This matrix must be multiplied by the residual variance to get the covariance of the parameter estimates – see curve_fit.
#~
    #~ infodict : dict
        #~ a dictionary of optional outputs with the key s:
        #~ nfev: The number of function calls
        #~ fvec: The function evaluated at the output
        #~ fjac: A permutation of the R matrix of a QR factorization of the final approximate Jacobian matrix, stored column wise. Together with ipvt, the covariance of the estimate can be approximated.
        #~ ipvt: An integer array of length N which defines a permutation matrix, p, such that fjac*p = q*r, where r is upper triangular with diagonal elements of nonincreasing magnitude. Column j of p is column ipvt(j) of the identity matrix.
        #~ qtf: The vector (transpose(q) * fvec).
#~
    #~ mesg : str
        #~ A string message giving information about the cause of failure.
#~
    #~ ier : int
        #~ An integer flag. If it is equal to 1, 2, 3 or 4, the solution was found. Otherwise, the solution was not found. In either case, the optional output variable ‘mesg’ gives more information.


# NOTE: the following needs scipy.version.version >= 0.17.0
#~ the call to least_squares returns scipy.optimize.OptimizeResult
#~ scipy.optimize.least_squares(
    #~ fun,
    #~ x0,
    #~ jac='2-point',
    #~ bounds=(-inf, inf),
    #~ method='trf',
    #~ ftol=1e-08,
    #~ xtol=1e-08,
    #~ gtol=1e-08,
    #~ x_scale=1.0,
    #~ loss='linear',
    #~ f_scale=1.0,
    #~ diff_step=None,
    #~ tr_solver=None,
    #~ tr_options={},
    #~ jac_sparsity=None,
    #~ max_nfev=None,
    #~ verbose=0,
    #~ args=(),
    #~ kwargs={})
# fun : callable
# Function which computes the vector of residuals, with the signature
# fun(x, *args, **kwargs), i.e., the minimization proceeds with respect to
# its first argument. The argument x passed to this function is an ndarray
# of shape (n,) (never a scalar, even for n=1). It must return a 1-d
# array_like of shape (m,) or a scalar.

# x0 : array_like with shape (n,) or float -- initial guess on independent
# variables. If float, it will be treated as a 1-d array with one element.

# OPTIONAL
# jac : {‘2-point’, ‘3-point’, ‘cs’, callable}, optional  Method of
# computing the Jacobian matrix (an m-by-n matrix, where element (i, j) is
# the partial derivative of f[i] with respect to x[j]). The keywords
# select a finite difference scheme for numerical estimation. The scheme
# ‘3-point’ is more accurate, but requires twice as much operations
# compared to ‘2-point’ (default). The scheme ‘cs’ uses complex steps, and
# while potentially the most accurate, it is applicable only when fun
# correctly handles complex inputs and can be analytically continued to
# the complex plane. Method ‘lm’ always uses the ‘2-point’ scheme. If
# callable, it is used as jac(x, *args, **kwargs) and should return a good
# approximation (or the exact value) for the Jacobian as an array_like
# (np.atleast_2d is applied), a sparse matrix or a
# scipy.sparse.linalg.LinearOperator.

# bounds : 2-tuple of array_like, optional Lower and upper bounds on
# independent variables. Defaults to no bounds. Each array must match the
# size of x0 or be a scalar, in the latter case a bound will be the same
# for all variables. Use np.inf with an appropriate sign to disable bounds
# on all or some variables.

# method : {‘trf’, ‘dogbox’, ‘lm’}, optional ‘trf’ :DEFAULT  Trust Region Reflective algorithm, particularly suitable for large sparse problems with bounds. Generally robust method.
#                ‘dogbox’ : dogleg algorithm with rectangular trust regions, typical use case is small problems with bounds. Not recommended for problems with rank-deficient Jacobian.
#                ‘lm’ : Levenberg-Marquardt algorithm as implemented in MINPACK. Doesn’t handle bounds and sparse Jacobians. Usually the most efficient method for small unconstrained problems.

# ftol : float, optional
# Tolerance for termination by the change of the cost function. Default is
# 1e-8. The optimization process is stopped when dF < ftol * F, and there
# was an adequate agreement between a local quadratic model and the true
# model in the last step.

# xtol : float, optional
#        Tolerance for termination by the change of the independent variables. Default is 1e-8. The exact condition depends on the method used:
#                For ‘trf’ and ‘dogbox’ : norm(dx) < xtol * (xtol + norm(x))
# For ‘lm’ : Delta < xtol * norm(xs), where Delta is a trust-region radius
# and xs is the value of x scaled according to x_scale parameter (see
# below).

# gtol : float, optional
#        Tolerance for termination by the norm of the gradient. Default is 1e-8. The exact condition depends on a method used:
#                For ‘trf’ : norm(g_scaled, ord=np.inf) < gtol, where g_scaled is the value of the gradient scaled to account for the presence of the bounds [STIR].
#                For ‘dogbox’ : norm(g_free, ord=np.inf) < gtol, where g_free is the gradient with respect to the variables which are not in the optimal state on the boundary.
# For ‘lm’ : the maximum absolute value of the cosine of angles between
# columns of the Jacobian and the residual vector is less than gtol, or
# the residual vector is zero.

# x_scale : array_like or ‘jac’, optional
# Characteristic scale of each variable. Setting x_scale is equivalent to
# reformulating the problem in scaled variables xs = x / x_scale. An
# alternative view is that the size of a trust region along j-th dimension
# is proportional to x_scale[j]. Improved convergence may be achieved by
# setting x_scale such that a step of a given size along any of the scaled
# variables has a similar effect on the cost function. If set to ‘jac’,
# the scale is iteratively updated using the inverse norms of the columns
# of the Jacobian matrix (as described in [JJMore]).

# loss : str or callable, optional
#        Determines the loss function. The following keyword values are allowed:
#                ‘linear’ (default) : rho(z) = z. Gives a standard least-squares problem.
#                ‘soft_l1’ : rho(z) = 2 * ((1 + z)**0.5 - 1). The smooth approximation of l1 (absolute value) loss. Usually a good choice for robust least squares.
#                ‘huber’ : rho(z) = z if z <= 1 else 2*z**0.5 - 1. Works similarly to ‘soft_l1’.
#                ‘cauchy’ : rho(z) = ln(1 + z). Severely weakens outliers influence, but may cause difficulties in optimization process.
#                ‘arctan’ : rho(z) = arctan(z). Limits a maximum loss on a single residual, has properties similar to ‘cauchy’.
# If callable, it must take a 1-d ndarray z=f**2 and return an array_like
# with shape (3, m) where row 0 contains function values, row 1 contains
# first derivatives and row 2 contains second derivatives. Method ‘lm’
# supports only ‘linear’ loss.

# f_scale : float, optional
# Value of soft margin between inlier and outlier residuals, default is
# 1.0. The loss function is evaluated as follows rho_(f**2) = C**2 *
# rho(f**2 / C**2), where C is f_scale, and rho is determined by loss
# parameter. This parameter has no effect with loss='linear', but for
# other loss values it is of crucial importance.

# max_nfev : None or int, optional
#        Maximum number of function evaluations before the termination. If None (default), the value is chosen automatically:
#                For ‘trf’ and ‘dogbox’ : 100 * n.
# For ‘lm’ : 100 * n if jac is callable and 100 * n * (n + 1) otherwise
# (because ‘lm’ counts function calls in Jacobian estimation).

# diff_step : None or array_like, optional
# Determines the relative step size for the finite difference
# approximation of the Jacobian. The actual step is computed as x *
# diff_step. If None (default), then diff_step is taken to be a
# conventional “optimal” power of machine epsilon for the finite
# difference scheme used [NR].

# tr_solver : {None, ‘exact’, ‘lsmr’}, optional
#        Method for solving trust-region subproblems, relevant only for ‘trf’ and ‘dogbox’ methods.
#                ‘exact’ is suitable for not very large problems with dense Jacobian matrices. The computational complexity per iteration is comparable to a singular value decomposition of the Jacobian matrix.
#                ‘lsmr’ is suitable for problems with sparse and large Jacobian matrices. It uses the iterative procedure scipy.sparse.linalg.lsmr for finding a solution of a linear least-squares problem and only requires matrix-vector product evaluations.
 # If None (default) the solver is chosen based on the type of Jacobian
 # returned on the first iteration.

# tr_options : dict, optional
#        Keyword options passed to trust-region solver.
#                tr_solver='exact': tr_options are ignored.
# tr_solver='lsmr': options for scipy.sparse.linalg.lsmr. Additionally
# method='trf' supports ‘regularize’ option (bool, default is True) which
# adds a regularization term to the normal equation, which improves
# convergence if the Jacobian is rank-deficient [Byrd] (eq. 3.4).

# jac_sparsity : {None, array_like, sparse matrix}, optional
# Defines the sparsity structure of the Jacobian matrix for finite
# difference estimation, its shape must be (m, n). If the Jacobian has
# only few non-zero elements in each row, providing the sparsity structure
# will greatly speed up the computations [Curtis]. A zero entry means that
# a corresponding element in the Jacobian is identically zero. If
# provided, forces the use of ‘lsmr’ trust-region solver. If None
# (default) then dense differencing will be used. Has no effect for ‘lm’
# method.

# verbose : {0, 1, 2}, optional
#        Level of algorithm’s verbosity:
#                0 (default) : work silently.
#                1 : display a termination report.
# 2 : display progress during iterations (not supported by ‘lm’ method).

# args, kwargs : tuple and dict, optional
# Additional arguments passed to fun and jac. Both empty by default. The
# calling signature is fun(x, *args, **kwargs) and the same for jac.

import numpy as np
from typing import List
from fixedincomelib.utilities import *


def qfCreate1DInterpolator(
    axis1: np.ndarray | List,
    values: np.ndarray | List,
    interp_method: str,
    extrap_method: str):

    interp_method_ = InterpMethod.from_string(interp_method)
    extrap_method_ = ExtrapMethod.from_string(extrap_method)

    return InterpolatorFactory.create_1d_interpolator(
        axis1, values, interp_method_, extrap_method_
    )


def qfInterpolate1D(x: float, interpolator1D: Interpolator1D):
    return interpolator1D.interpolate(x)


def qfInterpolate1DGrad(x: float, interpolator1D: Interpolator1D):
    return interpolator1D.gradient_wrt_ordinate(x)


def qfInterpolate1DIntegral(start_x: float, end_x: float, interpolator1D: Interpolator1D):
    return interpolator1D.integrate(start_x, end_x)


def qfInterpolate1DIntegralGrad(start_x: float, end_x: float, interpolator1D: Interpolator1D):
    return interpolator1D.gradient_of_integrated_value_wrt_ordinate(start_x, end_x)

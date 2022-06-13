# -*- coding: utf-8 -*-
"""Tools to check compatibility of EKO and grid."""
import numpy as np


def in1d(a, b, rtol=1e-05, atol=1e-08):
    """Improved version of np.in1d.

    Thanks: https://github.com/numpy/numpy/issues/7784#issuecomment-848036186

    Parameters
    ----------
    a : list
        needle
    b : list
        haystack
    rtol : float
        allowed relative error
    atol : float
        allowed absolute error

    Returns
    -------
    list
        mask of found elements
    """
    if len(a) == 1:
        for be in b:
            if np.isclose(be, a[0], rtol=rtol, atol=atol):
                return [True]
        return [False]
    ss = np.searchsorted(a[1:-1], b, side="left")
    return np.isclose(a[ss], b, rtol=rtol, atol=atol) | np.isclose(
        a[ss + 1], b, rtol=rtol, atol=atol
    )


def check_grid_and_eko_compatible(pineappl_grid, operators, xif):
    """Check whether the EKO operators and the PineAPPL grid are compatible.

    Parameters
    ----------
    pineappl_grid : pineappl.grid.Grid
        grid
    operators : eko.output.Output
        operators
    xif : float
        factorization scale variation

    Raises
    ------
    ValueError
        If the operators and the grid are not compatible.
    """
    x_grid, _pids, _mur2_grid, muf2_grid = pineappl_grid.axes()
    # Q2 grid
    if not np.all(
        in1d(
            np.unique(list(operators["Q2grid"].keys())), xif * xif * np.array(muf2_grid)
        )
    ):
        raise ValueError(
            "Q2 grid in pineappl grid and eko operator are NOT compatible!"
        )
    # x-grid
    if not np.all(in1d(np.unique(operators["targetgrid"]), np.array(x_grid))):
        raise ValueError("x grid in pineappl grid and eko operator are NOT compatible!")


def check_grid_contains_sv(pineappl_grid, xir, xif, ftr):
    """Raises a `ValueError if the theory_card asks for scale-variations but they are not
    available in the pineappl grid.

    Parameters
    ----------
        pineappl_grid : pineappl.grid.Grid
            grid
        xir : float
            log of renormalization scale ratio to central 
        xif : float
            log of factorization scale ratio to central (scheme-C)
        ftr : float
            log of factorization scale ratio to central (scheme-B)     
    """
    if xir == 1 and xif == 1 and ftr == 1:
        return 0
    order_list = [order.as_tuple() for order in pineappl_grid.orders()]
    for order in order_list:
        if order[-1] != 0 or order[-2] != 0:
            return 0
    raise ValueError(
        "Theory card is requesting scale variations but they are not available for this grid!"
    )

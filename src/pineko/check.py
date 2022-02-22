# -*- coding: utf-8 -*-
import numpy as np


def in1d(a, b, rtol=1e-05, atol=1e-08):
    """
    Improved version of np.in1d.

    Thanks: https://github.com/numpy/numpy/issues/7784#issuecomment-848036186
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


def check_grid_and_eko_compatible(pineappl_grid, operators):
    """
    Raises a `ValueError` if the EKO operators and the PineAPPL grid are NOT compatible.

    Parameters
    ----------
        pineappl_grid : pineappl.grid.Grid
            grid
        operators : eko.output.Output
            operators
    """
    x_grid, _pids, muf2_grid = pineappl_grid.axes()
    # Q2 grid
    if not np.all(
        in1d(np.unique(list(operators["Q2grid"].keys())), np.array(muf2_grid))
    ):
        raise ValueError(
            "Q2 grid in pineappl grid and eko operator are NOT compatible!"
        )
    # x-grid
    if not np.all(in1d(np.unique(operators["targetgrid"]), np.array(x_grid))):
        raise ValueError("x grid in pineappl grid and eko operator are NOT compatible!")

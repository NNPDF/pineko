"""Tools to check compatibility of EKO and grid."""
from collections import namedtuple
from dataclasses import dataclass
from enum import Enum, auto

import numpy as np
import pineappl


@dataclass
class ScaleValue:
    descr: str
    index: int


class Scale(Enum):
    """Auxiliary class to list the possible scale variations."""

    REN = ScaleValue("renormalization scale variations", -2)
    FACT = ScaleValue("factorization scale variations", -1)


class CheckMax(Enum):
    BOTH = auto()
    CENTRAL = auto()
    SCVAR = auto()


@dataclass
class OrderAvailable:
    """Collect the possible results of a scale variations check."""

    sv_as: bool
    sv_al: bool
    central_as: bool
    central_al: bool


def islepton(el):
    """Return True if el is a lepton PID, otherwise return False."""
    if 10 < abs(el) < 17:
        return True
    return False


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
    operators : eko.EKO
        operators
    xif : float
        factorization scale variation

    Raises
    ------
    ValueError
        If the operators and the grid are not compatible.
    """
    # Note that this is enough but once we consider max_al different
    # from 0, it will be better to use the actual order_mask
    mock_order_mask = np.array([True for _ord in pineappl_grid.orders()])
    evolve_info = pineappl_grid.raw.evolve_info(mock_order_mask)
    x_grid = evolve_info.x1
    muf2_grid = evolve_info.fac1
    # Q2 grid
    if not np.all(
        in1d(np.unique(list(operators.mu2grid)), xif * xif * np.array(muf2_grid))
    ):
        raise ValueError(
            "Q2 grid in pineappl grid and eko operator are NOT compatible!"
        )
    # x-grid
    if not np.all(
        in1d(np.unique(operators.rotations.targetgrid.tolist()), np.array(x_grid))
    ):
        raise ValueError("x grid in pineappl grid and eko operator are NOT compatible!")


def is_fonll_b(fns, lumi):
    """Check if the fktable we are computing is a DIS FONLL-B fktable.

    Parameters
    ----------
    fns : str
          flavor number scheme (from the theory card)
    lumi : list(list(tuple))
           luminosity info

    Returns
    -------
    bool
        true if the fktable is a FONLL-B DIS fktable
    """
    for lists in lumi:
        for el in lists:
            if (not islepton(el[0])) and (not islepton(el[1])):
                # in this case we are sure it is not DIS so for sure it is not FONLL-B
                return False
    if fns == "FONLL-B":
        return True
    return False


def get_orders_and_min(grid, max_as, max_al):
    """Return the alpha_s and alpha_l orders separately and the min_as and min_al appearing in the orders."""
    order_array = np.array([order.as_tuple() for order in grid.orders()])
    order_mask = pineappl.grid.Order.create_mask(grid.orders(), max_as, max_al)
    order_list = order_array[order_mask]
    as_orders = []
    al_orders = []
    min_al = min(ord[1] for ord in order_list)
    for order in order_list:
        if order[1] == min_al:
            as_orders.append(order)
    return as_orders


def contains_sv(grid, max_as, max_al, sv_type: Scale):
    """Check whether renormalization scale-variations are available in the pineappl grid.

    Parameters
    ----------
    grid : pineappl.grid.Grid
           Pineappl grid
    max_as : int
             max as order
    max_al : int
             max al order
    sv_type : Scale
        kind of scale_variation to be checked (either REN or FACT)

    Returns
    -------
    : CheckMax
        result of the check
    : int
        effective max_as in the grid
    """
    index_to_check = sv_type.value.index
    as_orders = get_orders_and_min(grid, max_as, max_al)
    max_as_effective = max(ord[0] for ord in as_orders)
    max_as_effective_cen = max(
        ord[0] for ord in as_orders if ord[index_to_check] == 0
    )
    max_as_effective_sv = max(
        (ord[0] for ord in as_orders if ord[index_to_check] != 0), default=0
    )
    if max_as_effective_cen == max_as_effective:
        if max_as_effective_sv == max_as_effective:
            checkres = CheckMax.BOTH
        else:
            checkres = CheckMax.CENTRAL
    else:
        checkres = CheckMax.SCVAR
    return checkres, max_as_effective

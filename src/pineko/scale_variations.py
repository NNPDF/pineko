"""Module to generate scale variations."""
import pathlib
from enum import Enum
from typing import Dict, List, Optional, Tuple

import numpy as np
import pineappl
from eko import beta

from . import check

AS_NORM = 1.0 / (4.0 * np.pi)
OrderTuple = Tuple[int, int, int, int]
"""Tuple representing a PineAPPL order."""


class ReturnState(Enum):
    """Auxiliary class to list the possible return states."""

    ALREADY_THERE = "[green]Renormalization scale variations are already in the grid"
    ORDER_EXISTS_FAILURE = (
        "Order_exists is True but the order does not appear to be in the grid"
    )
    MISSING_CENTRAL = "Central order is not high enough to compute requested sv orders"
    SUCCESS = "[green]Success: scale variation orders included!"


def qcd(order: OrderTuple) -> int:
    """Extract the QCD order from an OrderTuple."""
    return order[0]


def ren_sv_coeffs(m, max_as, logpart, which_part, nf):
    """Ren_sv coefficient for the requested part.

    Parameters
    ----------
    m : int
        first non zero perturbative order
    max_as : int
        max order of alpha_s
    logpart : int
        power of the renormalization scale log asked
    which_part : int
        asked perturbative order contribution to be rescaled
    nf : int
        number of active flavors

    Returns
    -------
    float
        renormalization scale variation contribution
    """
    bcoeff = beta.beta_qcd((max_as - logpart - which_part + 2, 0), nf)
    as_normalization = AS_NORM ** (max_as - which_part)
    if max_as == 0:
        return 0.0
    if max_as == 2:
        if which_part > 0:
            m += 1
        elif logpart > 1:
            m = 0.5 * m * (m + 1)
    return m * as_normalization * bcoeff


def requirements(m: int, max_as: int, al: int) -> Dict[OrderTuple, List[OrderTuple]]:
    """Compute a dictionary with all the necessary orders to compute to have the full renormalization scale variation.

    `m` is the first non-zero perturbative order of the grid, and `al` is the QED order of the "QCD" leading order.

    """
    return {
        (m + max_as, al, delt + 1, 0): [
            (m + de, al, 0, 0) for de in range(max_as - delt)
        ]
        for delt in range(max_as)
    }


def initialize_new_grid(grid, new_order):
    """Initialize a new grid only containing one order and with the same setting of an original grid."""
    # Retrieve parameters to create new grid
    bin_limits = [
        float(bin) for bin in range(grid.bins() + 1)
    ]  # The +1 explanation is that n bins have n+1 bin limits, and range generates numbers from a half-open interval (range(n) generates n numbers).
    lumi_grid = [pineappl.lumi.LumiEntry(mylum) for mylum in grid.lumi()]
    subgrid_params = pineappl.subgrid.SubgridParams()
    new_order = [pineappl.grid.Order(*new_order)]
    # create new_grid with same lumi and bin_limits of the original grid but with new_order
    new_grid = pineappl.grid.Grid.create(
        lumi_grid, new_order, bin_limits, subgrid_params
    )
    return new_grid


def create_svonly(grid, order, new_order, scalefactor):
    """Create a grid containing only the renormalization scale variations at a given order for a grid."""
    new_grid = initialize_new_grid(grid, new_order)
    # extract the relevant order to rescale from the grid for each lumi and bin
    grid_orders = [order.as_tuple() for order in grid.orders()]
    order_index = grid_orders.index(order)
    for lumi_index in range(len(new_grid.lumi())):
        for bin_index in range(grid.bins()):
            extracted_subgrid = grid.subgrid(order_index, bin_index, lumi_index)
            extracted_subgrid.scale(scalefactor)
            # Set this subgrid inside the new grid
            new_grid.set_subgrid(0, bin_index, lumi_index, extracted_subgrid)
    # Fixing bin_limits and normalizations
    bin_dimension = grid.bin_dimensions()
    limits = []
    for num_bin in range(grid.bins()):
        for dim in range(bin_dimension):
            limits.append((grid.bin_left(dim)[num_bin], grid.bin_right(dim)[num_bin]))
    norma = grid.bin_normalizations()
    remap_obj = pineappl.bin.BinRemapper(norma, limits)
    new_grid.set_remapper(remap_obj)
    return new_grid


def create_grids(gridpath, max_as, nf):
    """Create all the necessary scale variations grids for a certain starting grid."""
    grid = pineappl.grid.Grid.read(gridpath)
    grid_orders = [orde.as_tuple() for orde in grid.orders()]
    order_mask = pineappl.grid.Order.create_mask(grid.orders(), max_as, 0, True)
    grid_orders_filtered = list(np.array(grid_orders)[order_mask])
    grid_orders_filtered.sort(key=qcd)
    first_nonzero_order = grid_orders_filtered[0]
    min_al = first_nonzero_order[1]
    m_value = first_nonzero_order[0]
    nec_orders = requirements(m_value, max_as, min_al)
    grid_list = {}
    for to_construct_order in nec_orders:
        list_grid_order = []
        for nec_order in nec_orders[to_construct_order]:
            # The logpart of the coefficient I am asking is just the [2] entry of to_construct_order
            # The QCD order of the part I am rescaling is just nec_order[0] but I need to rescale it with respect to the first non-zero order
            scalefactor = ren_sv_coeffs(
                m_value, max_as, to_construct_order[2], nec_order[0] - m_value, nf
            )
            list_grid_order.append(
                create_svonly(grid, nec_order, to_construct_order, scalefactor)
            )
        grid_list[to_construct_order] = list_grid_order

    return grid_list, nec_orders


def write_grids(gridpath, grid_list):
    """Write the single grids."""
    base_name = gridpath.stem.split(".pineappl")[0]
    final_part = ".pineappl.lz4"
    grid_paths = []
    for order in grid_list:
        # For each scale variation order, if more than one grid contributes, merge them all together in a single one
        if len(grid_list[order]) > 1:
            for grid in grid_list[order][1:]:
                tmp_path = gridpath.parent / ("tmp" + final_part)
                grid.write_lz4(tmp_path)
                grid_list[order][0].merge_from_file(tmp_path)
                tmp_path.unlink()
        new_grid_path = gridpath.parent / (
            base_name + "_" + str(order[2]) + final_part
        )  # order[2] is the ren_sv order
        grid_paths.append(new_grid_path)
        grid_list[order][0].write_lz4(new_grid_path)
    return grid_paths


def merge_grids(
    gridpath, grid_list_path, target_path=None, nec_orders=None, order_exists=False
):
    """Merge the single grids in the original."""
    grid = pineappl.grid.Grid.read(gridpath)
    if target_path is None:
        target_path = gridpath.parent / gridpath.name
    else:
        target_path = target_path / gridpath.name
    if order_exists:
        grid = construct_and_dump_order_exists_grid(
            grid, list(nec_orders.keys())[0] if nec_orders is not None else []
        )
    for grid_path in grid_list_path:
        grid.merge_from_file(grid_path)
        grid_path.unlink()
    grid.write_lz4(target_path)


def construct_and_dump_order_exists_grid(ori_grid, to_construct_order):
    """Remove the order that has to be substituted from the grid."""
    bin_limits = [float(bin) for bin in range(ori_grid.bins() + 1)]
    lumi_grid = [pineappl.lumi.LumiEntry(mylum) for mylum in ori_grid.lumi()]
    subgrid_params = pineappl.subgrid.SubgridParams()
    ori_grid_orders = [order.as_tuple() for order in ori_grid.orders()]
    new_orders = [
        pineappl.grid.Order(*ord)
        for ord in ori_grid_orders
        if ord != to_construct_order
    ]
    new_grid = pineappl.grid.Grid.create(
        lumi_grid, new_orders, bin_limits, subgrid_params
    )
    orders_indeces = [ori_grid_orders.index(order.as_tuple()) for order in new_orders]
    for order_index in orders_indeces:
        for lumi_index in range(len(lumi_grid)):
            for bin_index in range(ori_grid.bins()):
                extr_subgrid = ori_grid.subgrid(order_index, bin_index, lumi_index)
                new_grid.set_subgrid(
                    orders_indeces.index(order_index),
                    bin_index,
                    lumi_index,
                    extr_subgrid,
                )
    bin_dimension = ori_grid.bin_dimensions()
    limits = []
    for num_bin in range(ori_grid.bins()):
        for dim in range(bin_dimension):
            limits.append(
                (
                    ori_grid.bin_left(dim)[num_bin],
                    ori_grid.bin_right(dim)[num_bin],
                )
            )
    norma = ori_grid.bin_normalizations()
    remap_obj = pineappl.bin.BinRemapper(norma, limits)
    new_grid.set_remapper(remap_obj)
    new_grid.set_key_value("initial_state_2", ori_grid.key_values()["initial_state_2"])
    return new_grid


def compute_ren_sv_grid(
    grid_path: pathlib.Path,
    max_as: int,
    nf: int,
    target_path: Optional[pathlib.Path] = None,
    order_exists: bool = False,
):
    """Generate renormalization scale variation terms for the given grid, according to the max_as."""
    # First let's check if the ren_sv are already there
    checkres, max_as_effective = check.contains_sv(
        pineappl.grid.Grid.read(grid_path), max_as, 0, check.Scale.REN
    )
    # Usual different convention with max_as
    if max_as_effective == max_as and (checkres is not check.AvailableAtMax.CENTRAL):
        if not order_exists:
            return ReturnState.ALREADY_THERE
    elif order_exists:
        return ReturnState.ORDER_EXISTS_FAILURE
    if max_as_effective < max_as and checkres is check.AvailableAtMax.SCVAR:
        return ReturnState.MISSING_CENTRAL
    # With respect to the usual convention here max_as is max_as-1
    max_as -= 1
    # Creating all the necessary grids
    grid_list, nec_orders = create_grids(grid_path, max_as, nf)
    # Writing the sv grids
    sv_grids_paths = write_grids(gridpath=grid_path, grid_list=grid_list)
    # Merging all together
    merge_grids(
        gridpath=grid_path,
        grid_list_path=sv_grids_paths,
        target_path=target_path,
        nec_orders=nec_orders,
        order_exists=order_exists,
    )
    return ReturnState.SUCCESS

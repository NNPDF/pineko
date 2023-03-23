"""Module to generate scale variations."""
import pathlib

import numpy as np
import pineappl
import rich
from eko import beta

from . import check

AS_NORM = 1.0 / (4.0 * np.pi)


def sort_orders(order):
    """Define the sorting for an order. In particular the order is sorted according to the as order."""
    return order[0]


def ren_sv_coeffs(m, max_as, logpart, which_part, nf):
    """Return the ren_sv contribution relative to the requested log power and perturbative order contribution (which_part).

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
    if max_as == 0:
        return 0.0
    elif max_as == 1:
        return -(-m * beta.beta_qcd((2, 0), nf) * AS_NORM)
    elif max_as == 2:
        if which_part == 0:
            if logpart == 1:
                return m * beta.beta_qcd((3, 0), nf) * (AS_NORM**2)
            else:
                return (
                    0.5
                    * m
                    * (m + 1)
                    * (beta.beta_qcd((2, 0), nf) ** 2)
                    * (AS_NORM**2)
                )
        else:
            return (m + 1) * beta.beta_qcd((2, 0), nf) * AS_NORM


def compute_scale_factor(m, nec_order, to_construct_order, nf):
    """Compute the factor of renormalization scale variation.

    Parameters
    ----------
    m : int
        first non zero perturbative order
    nec_order : tuple(int)
        tuple of the order that has to be rescaled to get the scale varied order
    to_contruct_order : tuple(int)
        tuple of the scale varied order to be constructed
    nf : int
        number of active flavors

    Returns
    -------
    float
        full contribution of ren sv
    """
    max_as = to_construct_order[0] - m
    logpart = to_construct_order[2]
    return ren_sv_coeffs(m, max_as, logpart, nec_order[0] - m, nf)


def compute_orders_map(m, max_as, min_al):
    """Compute a dictionary with all the necessary orders to compute to have the full renormalization scale variation.

    Parameters
    ----------
    m : int
        first non zero perturbative order of the grid
    max_as : int
        max alpha_s order
    min_al : int
        al order of leading order
    Returns
    -------
    dict(tuple(int))
        description of all the needed orders
    """
    orders = {}
    for delt in range(max_as):
        orders[(m + max_as, min_al, delt + 1, 0)] = [
            (m + de, min_al, 0, 0) for de in range(max_as - delt)
        ]
    return orders


def create_svonly(grid, order, new_order, scalefactor):
    """Create a grid containing only the renormalization scale variations at a given order for a grid."""
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
    # extract the relevant order to rescale from the grid for each lumi and bin
    grid_orders = [order.as_tuple() for order in grid.orders()]
    order_index = grid_orders.index(order)
    for lumi_index in range(len(lumi_grid)):
        for bin_index in range(grid.raw.bins()):
            extracted_subgrid = grid.subgrid(order_index, bin_index, lumi_index)
            extracted_subgrid.scale(scalefactor)
            # Set this subgrid inside the new grid
            new_grid.set_subgrid(0, bin_index, lumi_index, extracted_subgrid)
    # Fixing bin_limits and normalizations
    bin_dimension = grid.raw.bin_dimensions()
    limits = []
    for num_bin in range(grid.raw.bins()):
        for dim in range(bin_dimension):
            limits.append(
                (grid.raw.bin_left(dim)[num_bin], grid.raw.bin_right(dim)[num_bin])
            )
    norma = grid.raw.bin_normalizations()
    remap_obj = pineappl.bin.BinRemapper(norma, limits)
    new_grid.set_remapper(remap_obj)
    return new_grid


def create_grids(gridpath, max_as, nf):
    """Create all the necessary scale variations grids for a certain starting grid."""
    grid = pineappl.grid.Grid.read(gridpath)
    grid_orders = [orde.as_tuple() for orde in grid.orders()]
    order_mask = pineappl.grid.Order.create_mask(grid.orders(), max_as, 0)
    grid_orders_filtered = list(np.array(grid_orders)[order_mask])
    grid_orders_filtered.sort(key=sort_orders)
    first_nonzero_order = grid_orders_filtered[0]
    min_al = first_nonzero_order[1]
    m_value = first_nonzero_order[0]
    nec_orders = compute_orders_map(m_value, max_as, min_al)
    grid_list = {}
    for to_construct_order in nec_orders:
        list_grid_order = []
        for nec_order in nec_orders[to_construct_order]:
            scalefactor = compute_scale_factor(
                m_value, nec_order, to_construct_order, nf
            )
            list_grid_order.append(
                create_svonly(grid, nec_order, to_construct_order, scalefactor)
            )
        grid_list[to_construct_order] = list_grid_order

    return grid_list


def write_sv_grids(gridpath, grid_list):
    """Write the scale variations grids."""
    base_name = gridpath.stem.split(".pineappl")[0]
    final_part = ".pineappl.lz4"
    grid_paths = []
    for order in grid_list:
        # For each scale variation order, if more than one grid contributes, merge them all together in a single one
        if len(grid_list[order]) > 1:
            for grid in grid_list[order][1:]:
                tmp_path = gridpath.parent / ("tmp" + final_part)
                grid.raw.write_lz4(tmp_path)
                grid_list[order][0].raw.merge_from_file(tmp_path)
                tmp_path.unlink()
        new_grid_path = gridpath.parent / (
            base_name + "_" + str(order[2]) + final_part
        )  # order[2] is the ren_sv order
        grid_paths.append(new_grid_path)
        grid_list[order][0].raw.write_lz4(new_grid_path)
    return grid_paths


def merge_grids(gridpath, grid_list_path, target_path=None):
    """Merge the scale variations grids in the original."""
    grid = pineappl.grid.Grid.read(gridpath)
    if target_path is None:
        base_name = gridpath.stem.split(".pineappl")[0]
        target_path = gridpath.parent / (base_name + "_plusrensv.pineappl.lz4")
    for grid_path in grid_list_path:
        grid.raw.merge_from_file(grid_path)
        grid_path.unlink()
    grid.raw.write_lz4(target_path)


def compute_ren_sv_grid(grid_path, max_as, nf, target_path=None):
    """Generate renormalization scale variation terms for the given grid, according to the max_as.

    Parameters
    ----------
    grid_pah : pathlib.Path()
        pineappl grid path
    max_as : int
        max as order
    nf : int
        number of active flavors
    target_path: str
        path where store the new grid (optional)
    """
    # First let's check if the ren_sv are already there
    grid_path = pathlib.Path(grid_path)
    grid = pineappl.grid.Grid.read(grid_path)
    checkres, max_as_effective = check.contains_sv(grid, max_as, 0, check.Scale.REN)
    # Usual different convention with max_as
    if max_as_effective == max_as and (checkres is not check.AvailableAtMax.CENTRAL):
        rich.print(f"[green]Renormalization scale variations are already in the grid")
        return
    if max_as_effective < max_as and checkres is check.AvailableAtMax.SCVAR:
        raise ValueError(
            "Central order is not high enough to compute requested sv orders"
        )
    # With respect to the usual convention here max_as is max_as-1
    max_as = max_as - 1
    # Creating all the necessary grids
    grid_list = create_grids(grid_path, max_as, nf)
    # Writing the sv grids
    sv_grids_paths = write_sv_grids(gridpath=grid_path, grid_list=grid_list)
    # Merging all together
    merge_grids(
        gridpath=grid_path, grid_list_path=sv_grids_paths, target_path=target_path
    )

"""Module to generate scale variations."""
import pineappl
import rich
from eko import beta

from . import check


def ren_sv_coeffs(m, delta, logpart, which_part, nf):
    """Return the ren_sv contribution relative to the requested log power and perturbative order contribution (which_part).

    Parameters
    ----------
    m : int
        first non zero perturbative order
    delta : int
        difference between asked order and m
    logpart : int
        power of the log asked
    which_part : int
        asked perturbative order contribution
    nf : int
        number of active flavors

    Returns
    -------
    float
        renormalization scale variation contribution
    """
    if delta == 0:
        return 0.0
    elif delta == 1:
        return -m * beta.beta_qcd((2, 0), nf)
    elif delta == 2:
        if which_part == 0:
            if logpart == 1:
                return -m * beta.beta_qcd((3, 0), nf)
            else:
                return 0.5 * m * (m + 1) * (beta.beta_qcd((2, 0), nf) ** 2)
        else:
            return -(m + 1) * beta.beta_qcd((2, 0), nf)


def compute_scale_factor(m, nec_order, to_construct_order, nf, kR):
    """Compute the factor of renormalization scale variation.

    Parameters
    ----------
    m : int
        first non zero perturbative order
    nec_order : tuple(int)
        tuple of the order for which the sv contribution is asked for
    to_contruct_order : tuple(int)
        tuple of the sv order to be constructed
    nf : int
        number of active flavors
    kR : float
        log of the ratio between renormalization scale and Q

    Returns
    -------
    float
        full contribution of ren sv
    """
    delta = to_construct_order[0] - m
    logpart = to_construct_order[2]
    return (kR**logpart) * ren_sv_coeffs(m, delta, logpart, nec_order[0] - m, nf)


def compute_orders_map(m, delta):
    """Compute a dictionary with all the necessary order to compute in order to have the full renormalization scale variation.

    Parameters
    ----------
    m : int
        first non zero perturbative order
    delta : int
        difference between asked order and m

    Returns
    -------
    dict(tuple(int))
        description of all the needed orders
    """
    orders = {}
    for delt in range(delta):
        orders[(m + delta, 0, delt + 1, 0)] = [
            (m + de, 0, 0, 0) for de in range(delta - delt)
        ]
    return orders


def create_svonly_grid(grid, order, new_order, scalefactor):
    """Create a grid containing only the renormalization scale variations at a given order for a grid."""
    # Retrieve parameters to create new grid
    bin_limits = [
        float(bin) for bin in range(grid.raw.bins() + 1)
    ]  # +1 because I don't know
    lumi_grid = [pineappl.lumi.LumiEntry(mylum) for mylum in grid.raw.lumi()]
    subgrid_params = pineappl.subgrid.SubgridParams()
    new_order = [pineappl.grid.Order(*new_order)]
    # create new_grid with same lumi and bin_limits of the original grid but with new_order
    new_grid = pineappl.grid.Grid.create(
        lumi_grid, new_order, bin_limits, subgrid_params
    )
    # extract the relevant order to rescale from the grid for each lumi and bin
    grid_orders = [orde.as_tuple() for orde in grid.orders()]
    order_index = grid_orders.index(order)
    for lumi_index in range(len(lumi_grid)):
        for bin_index in range(grid.raw.bins()):
            extracted_subgrid = grid.subgrid(order_index, bin_index, lumi_index)
            extracted_subgrid.scale(scalefactor)
            # Set this subgrid inside the new grid
            new_grid.set_subgrid(0, bin_index, lumi_index, extracted_subgrid)
    return new_grid


def create_all_necessary_grids(gridpath, order, kR, nf):
    """Create all the necessary scale variations grids for a certain starting grid."""
    grid = pineappl.grid.Grid.read(gridpath)
    grid_orders = [orde.as_tuple() for orde in grid.orders()]
    first_nonzero_order = grid_orders[0]
    m_value = first_nonzero_order[0]
    deltaorder = order[0] - m_value
    nec_orders = compute_orders_map(m_value, deltaorder)
    grid_list = []
    for to_construct_order in nec_orders:
        for nec_order in nec_orders[to_construct_order]:
            scalefactor = compute_scale_factor(
                m_value, nec_order, to_construct_order, nf, kR
            )
            grid_list.append(
                create_svonly_grid(grid, nec_order, to_construct_order, scalefactor)
            )
    return grid_list


def construct_ren_sv_grid(grid, max_as, nf):
    """Generate renormalization scale variation terms for the given grid, according to the max_as.

    Parameters
    ----------
    grid : pineappl.grid.Grid
        pineappl grid
    max_as : int
        max as order
    nf : int
        number of active flavors
    """
    # First let's check if the ren_sv are already there
    sv_as, sv_al = check.contains_ren(grid, max_as, max_al=0)
    if sv_as:
        rich.print(f"[green]Renormalization scale variations are already in the grid")
    ### Extract the correct subgrid and call the function to scale it

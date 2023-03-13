"""Module to include k_factors in grids."""
import io
import pathlib

import eko
import lhapdf
import numpy as np
import pineappl
import rich
import yaml
from eko import beta

from . import check


def sort_orders(order):
    """Define the sorting for an order. In particular the order is sorted according only to the as order."""
    return order[0]


def read_kfactor(kfactor_path):
    """Read the k_factor and returns the central values and the pdfset used to compute it."""
    with open(kfactor_path, encoding="utf-8") as f:
        stars = f.readline()
        if not stars.startswith("*"):
            raise TypeError("First line should start with '*'.")
        descstring = io.StringIO()
        for line in f:
            if line.startswith("*"):
                break
            descstring.write(line)
        description = descstring.getvalue()
        try:
            data = np.loadtxt(f)
        except Exception as e:
            raise TypeError(e) from e
        data = data.reshape(-1, 2)
        central_value = data[:, 0]
        pdf_set = description.split(sep="PDFset:")[-1].split(sep="\n")[0].strip()
    return central_value, pdf_set


def compute_scale_factor(
    m, nec_order, to_construct_order, Q, central_k_factor, bin_index, alphas
):
    """Compute the factor to be multiplied to the given nec_order.

    Parameters
    ----------
    m : int
        first non zero perturbative order
    nec_order : tuple(int)
        tuple of the order that has to be rescaled to get the final order
    to_contruct_order : tuple(int)
        tuple of the scale varied order to be constructed
    Q: float
        energy scale of the bin
    central_k_factor: list(float)
        list of the centrals k_factors
    bin_index: int
        index of the bin
    alphas: lhapdf.AlphaS
        alpha_s object

    Returns
    -------
    float
        full contribution factor
    """
    max_as = to_construct_order[0] - m
    alpha_val = alphas.alphasQ(Q)
    alpha_term = (pow(4 * np.pi, max_as - (nec_order[0] - m))) / pow(
        alpha_val, max_as - (nec_order[0] - m)
    )
    k_term = central_k_factor[bin_index] - 1.0
    return k_term * alpha_term


def compute_orders_map(m, max_as, min_al):
    """Compute a dictionary with all the necessary orders to compute the requested order.

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
    orders[(m + max_as, min_al, 0, 0)] = [
        (m + de, min_al, 0, 0) for de in range(max_as)
    ]
    return orders


def create_singlegridonly(grid, m_value, order, new_order, central_k_factor, alphas):
    """Create a grid containing only the contribution given by new_order."""
    # Retrieve parameters to create new grid
    bin_limits = [
        float(bin) for bin in range(grid.raw.bins() + 1)
    ]  # The +1 explanation is that n bins have n+1 bin limits, and range generates numbers from a half-open interval (range(n) generates n numbers).
    lumi_grid = [pineappl.lumi.LumiEntry(mylum) for mylum in grid.raw.lumi()]
    subgrid_params = pineappl.subgrid.SubgridParams()
    new_order = [pineappl.grid.Order(*new_order)]
    new_order_tuple = [ord.as_tuple() for ord in new_order]
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
            Q = 10  # Just to see
            scalefactor = compute_scale_factor(
                m_value,
                order,
                new_order_tuple[0],
                Q,
                central_k_factor,
                bin_index,
                alphas,
            )
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


def create_grids(
    gridpath, max_as, first_non_zero_as_order, min_al, centrals_k_factor, alphas
):
    """Create all the necessary grids for a certain starting grid."""
    grid = pineappl.grid.Grid.read(gridpath)
    m_value = first_non_zero_as_order
    nec_orders = compute_orders_map(m_value, max_as, min_al)
    grid_list = {}
    for to_construct_order in nec_orders:
        list_grid_order = []
        for nec_order in nec_orders[to_construct_order]:
            list_grid_order.append(
                create_singlegridonly(
                    grid,
                    m_value,
                    nec_order,
                    to_construct_order,
                    centrals_k_factor,
                    alphas,
                )
            )
        grid_list[to_construct_order] = list_grid_order

    return grid_list


def write_grids(gridpath, grid_list):
    """Write the single grids."""
    base_name = gridpath.stem.split(".pineappl")[0]
    final_part = ".pineappl.lz4"
    grid_paths = []
    for order in grid_list:
        # For each order, if more than one grid contributes, merge them all together in a single one
        if len(grid_list[order]) > 1:
            for grid in grid_list[order][1:]:
                tmp_path = gridpath.parent / ("tmp" + final_part)
                grid.raw.write_lz4(tmp_path)
                grid_list[order][0].raw.merge_from_file(tmp_path)
                tmp_path.unlink()
        new_grid_path = gridpath.parent / (
            base_name + "_new_order" + final_part
        )  # order[2] is the ren_sv order
        grid_paths.append(new_grid_path)
        grid_list[order][0].raw.write_lz4(new_grid_path)
    return grid_paths


def merge_grids(gridpath, grid_list_path, target_path=None):
    """Merge the single grids in the original."""
    grid = pineappl.grid.Grid.read(gridpath)
    base_name = gridpath.stem.split(".pineappl")[0]
    target_name = base_name + "_pluskfactor.pineappl.lz4"
    if target_path is None:
        target_path = gridpath.parent / target_name
    else:
        target_path = target_path / target_name
    for grid_path in grid_list_path:
        grid.raw.merge_from_file(grid_path)
        grid_path.unlink()
    grid.raw.write_lz4(target_path)


def is_already_in(to_check, list_orders):
    """Check if the requested order is already in the grid."""
    is_in = False
    for order in list_orders:
        if order[-2] == 0 and order[-1] == 0:
            if (order[0] == to_check[0]) and (order[1] == to_check[1]):
                is_in = True
                return is_in
    return is_in


def compute_k_factor_grid(
    grids_folder, kfactor_folder, yamldb_path, compound_path, max_as, target_folder=None
):
    """Include the k_factor in the grid in order to have its associated order in the grid itself.

    Parameters
    ----------
    grids_folder : pathlib.Path()
        pineappl grids folder
    kfactor_folder : pathlib.Path()
        kfactors folder
    yamldb_path : pathlib.Path()
        path to the yaml file describing the dataset
    compound_path : pathlib.Path()
        path to the compound file if exists
    max_as : int
        max as order
    target_folder: pathlib.Path
        path where store the new grid (optional)
    """
    with open(yamldb_path, encoding="utf-8") as f:
        yamldict = yaml.safe_load(f)
    target_dataset = yamldict["target_dataset"]
    is_concatenated = False
    list_grids = []
    for op in yamldict["operands"]:
        list_grids.append(op[0])
    if len(list_grids) > 1:
        is_concatenated = True
    # if compound file exists, take cfactor file names from there.
    # If not then the cfactor file name can be obtained form the target dataset name alone.
    if compound_path is not None:
        cfac_names = [
            i[3:-4] for i in compound_path.read_text().split() if i.endswith(".dat")
        ]
        cfac_paths = [kfactor_folder / f"CF_QCD_{i}.dat" for i in cfac_names]
    else:
        cfac_paths = [kfactor_folder / f"CF_QCD_{target_dataset}.dat"]

    if not is_concatenated:
        grid_path = grids_folder / (f"{list_grids[0]}.pineappl.lz4")
        grid = pineappl.grid.Grid.read(grid_path)
        grid_orders = [orde.as_tuple() for orde in grid.orders()]
        order_mask = pineappl.grid.Order.create_mask(grid.orders(), max_as, 0)
        grid_orders_filtered = list(np.array(grid_orders)[order_mask])
        grid_orders_filtered.sort(key=sort_orders)
        first_nonzero_order = grid_orders_filtered[0]
        min_al = first_nonzero_order[1]
        # With respect to the usual convention here max_as is max_as-1
        max_as = max_as - 1
        if is_already_in(
            (first_nonzero_order[0] + max_as, min_al, 0, 0), grid_orders_filtered
        ):
            rich.print(f"[Success] Requested order already in the grid.")
            return
        # Reading the k_factor
        centrals_kfactor, pdf_set = read_kfactor(cfac_paths[0])
        alphas = lhapdf.mkAlphaS(pdf_set)
        # We need the pdf set to get the correct alpha values
        # Creating all the necessary grids
        grid_list = create_grids(
            grid_path, max_as, first_nonzero_order[0], min_al, centrals_kfactor, alphas
        )
        # Writing the sv grids
        grids_paths = write_grids(gridpath=grid_path, grid_list=grid_list)
        # Merging all together
        merge_grids(
            gridpath=grid_path, grid_list_path=grids_paths, target_path=target_folder
        )
    else:
        for grid_path, cfac_path in zip(list_grids, cfac_paths):
            print("Not yet implemented")

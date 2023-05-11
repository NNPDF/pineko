"""Module to include QCD K-factors in grids."""
import io
import pathlib

import numpy as np
import pineappl
import rich
import yaml
from pineappl import import_only_subgrid

from . import scale_variations

DEFAULT_PDF_SET = "NNPDF40_nnlo_as_01180"


def factgrid(subgrid):
    """Return the array of the factorization scales squared from a subgrid."""
    return np.array([mu2.fac for mu2 in subgrid.mu2_grid()])


def rengrid(subgrid):
    """Return the array of the renormalization scales squared from a subgrid."""
    return np.array([mu2.ren for mu2 in subgrid.mu2_grid()])


def read_kfactor(kfactor_path):
    """Read the k-factor and returns the central values and the pdfset used to compute it."""
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
        # If there is no PDF set in the k-factor, a default PDF set will be used
        # If the PDF set written in the file is not an actual lhapdf PDF, it will
        # raise an error.
        if len(pdf_set) == 0:
            pdf_set = DEFAULT_PDF_SET
    return central_value, pdf_set


def construct_scales_array(
    mu2_ren_grid,
    m_value,
    order,
    new_order,
    central_k_factor,
    bin_index,
    alphas,
    order_exists,
):
    """Construct the array that will rescale the subgrid array taking into account the different renormalization scales."""
    scales_array = []
    for mu2 in mu2_ren_grid:
        scales_array.append(
            compute_scale_factor(
                m_value,
                order,
                new_order,
                mu2,
                central_k_factor,
                bin_index,
                alphas,
                order_exists,
            )
        )
    return scales_array


def compute_scale_factor(
    m,
    nec_order,
    to_construct_order,
    Q2,
    central_k_factor,
    bin_index,
    alphas,
    order_exists,
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
    Q2: float
        energy scale squared of the bin
    central_k_factor: list(float)
        list of the centrals k-factors
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
    alpha_val = alphas.alphasQ2(Q2)
    alpha_term = 1.0 / pow(alpha_val, max_as - (nec_order[0] - m))
    k_term = central_k_factor[bin_index] - 1.0
    if order_exists and (max_as - (nec_order[0] - m)) == 0:
        k_term = central_k_factor[bin_index]
    return k_term * alpha_term


def scale_subgrid(extracted_subgrid, scales_array):
    """Rescales the array contained in the subgrid using scales_array and returns a new subgrid constructed with the scaled array."""
    original_array = extracted_subgrid.to_array3()
    if len(original_array) != len(scales_array):
        raise ValueError("The original and the scales arrays have different shapes.")
    scaled_array = []
    for scale_value, arr_to_scale in zip(scales_array, original_array):
        scaled_array_nest = []
        for arr in arr_to_scale:
            scaled_array_nest.append(list(arr * scale_value))
        scaled_array.append(scaled_array_nest)
    x1grid = extracted_subgrid.x1_grid()
    x2grid = extracted_subgrid.x2_grid()
    if len(scales_array) == 0:
        scaled_array = np.zeros(shape=(0, 0, 0), dtype=float)
    else:
        scaled_array = np.array(scaled_array, dtype=float)
    mu2_grid = [tuple([mu2.ren, mu2.fac]) for mu2 in extracted_subgrid.mu2_grid()]
    scaled_subgrid = import_only_subgrid.ImportOnlySubgridV2(
        scaled_array, mu2_grid, x1grid, x2grid
    )
    return scaled_subgrid


def compute_orders_map(m, max_as, min_al, order_exists):
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
    add = 0
    if order_exists:
        add = 1
    orders = {}
    orders[(m + max_as, min_al, 0, 0)] = [
        (m + de, min_al, 0, 0) for de in range(max_as + add)
    ]
    return orders


def create_singlegridonly(
    grid, m_value, order, new_order, central_k_factor, alphas, order_exists
):
    """Create a grid containing only the contribution given by new_order."""
    new_grid = scale_variations.initialize_new_grid(grid, new_order)
    # extract the relevant order to rescale from the grid for each lumi and bin
    grid_orders = [order.as_tuple() for order in grid.orders()]
    order_index = grid_orders.index(order)
    for lumi_index in range(len(new_grid.lumi())):
        for bin_index in range(grid.bins()):
            extracted_subgrid = grid.subgrid(order_index, bin_index, lumi_index)
            scales_array = construct_scales_array(
                rengrid(extracted_subgrid),
                m_value,
                order,
                new_order,
                central_k_factor,
                bin_index,
                alphas,
                order_exists,
            )
            scaled_subgrid = scale_subgrid(extracted_subgrid, scales_array)
            # Set this subgrid inside the new grid
            new_grid.set_subgrid(0, bin_index, lumi_index, scaled_subgrid)
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
    gridpath,
    max_as,
    first_non_zero_as_order,
    min_al,
    centrals_k_factor,
    alphas,
    order_exists,
):
    """Create all the necessary grids for a certain starting grid."""
    grid = pineappl.grid.Grid.read(gridpath)
    m_value = first_non_zero_as_order
    nec_orders = compute_orders_map(m_value, max_as, min_al, order_exists)
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
                    order_exists,
                )
            )
        grid_list[to_construct_order] = list_grid_order

    return grid_list, nec_orders


def is_already_in(to_check, list_orders):
    """Check if the requested order is already in the grid."""
    for order in list_orders:
        if (
            order[-2] == 0
            and order[-1] == 0
            and (order[0] == to_check[0])
            and (order[1] == to_check[1])
        ):
            return True
    return False


def construct_and_merge_grids(
    grid_path,
    max_as,
    first_nonzero_order,
    min_al,
    centrals_kfactor,
    alphas,
    target_folder,
    order_exists,
):
    """Create, write and merge all the grids."""
    # Creating all the necessary grids
    grid_list, nec_orders = create_grids(
        grid_path,
        max_as,
        first_nonzero_order[0],
        min_al,
        centrals_kfactor,
        alphas,
        order_exists,
    )
    # Writing the sv grids
    grids_paths = scale_variations.write_grids(gridpath=grid_path, grid_list=grid_list)
    # Merging all together
    scale_variations.merge_grids(
        gridpath=grid_path,
        grid_list_path=grids_paths,
        target_path=target_folder,
        nec_orders=nec_orders,
        order_exists=order_exists,
    )


def do_it(
    centrals_kfactor,
    alphas,
    grid_path,
    grid,
    max_as,
    max_as_test,
    target_folder,
    order_exists,
):
    """Apply the centrals_kfactor to the grid if the order is not already there."""
    grid_orders = [orde.as_tuple() for orde in grid.orders()]
    order_mask = pineappl.grid.Order.create_mask(grid.orders(), max_as, 0, True)
    grid_orders_filtered = list(np.array(grid_orders)[order_mask])
    grid_orders_filtered.sort(key=scale_variations.qcd)
    first_nonzero_order = grid_orders_filtered[0]
    min_al = first_nonzero_order[1]
    is_in = is_already_in(
        (first_nonzero_order[0] + max_as_test, min_al, 0, 0), grid_orders_filtered
    )
    if is_in and not order_exists:
        rich.print(f"[green] Success: Requested order already in the grid.")
        return
    elif not is_in and order_exists:
        rich.print(f"[red] Abort: order exists is True but order not in the grid.")
        return
    construct_and_merge_grids(
        grid_path,
        max_as_test,
        first_nonzero_order,
        min_al,
        centrals_kfactor,
        alphas,
        target_folder,
        order_exists,
    )


def filter_k_factors(pigrid, centrals_kfactor):
    """Filter the centrals k-factors according to their lenght compared to the number of bins of the grid."""
    centrals_kfactor_filtered = np.array([])
    if pigrid.bins() == len(centrals_kfactor):
        rich.print(f"[orange] The number of bins match the lenght of the k-factor.")
        centrals_kfactor_filtered = centrals_kfactor
    elif pigrid.bins() < len(centrals_kfactor):
        rich.print(
            f"[yellow] The number of bins is less than the lenght of the k-factor."
        )
        if not all(elem == centrals_kfactor[0] for elem in centrals_kfactor):
            # This case is actually wrong.
            raise ValueError("KFactor contains too many different values.")
        centrals_kfactor_filtered = centrals_kfactor
    else:
        rich.print(
            f"[yellow] The number of bins is more than the lenght of the k-factor."
        )

        # This is the last case in which grid.bins() > len(centrals_kfactor)

        # Note that sometimes there are more bins in the grid than in the cfactor file -
        # this is not a problem because in those cases either all cfactor values are the
        # same (thus there is no doubt about whether we have the correct one) or the
        # non-exisiting cfactors would be multiplied by bins corresponding to all '0' in the
        # grid.
        # Let's check if we are in the first or second case
        if len(np.unique(centrals_kfactor)) == 1:
            # In this case I just need to add more elements to the kfactor
            for _num in range(pigrid.bins()):
                centrals_kfactor_filtered = np.append(
                    centrals_kfactor_filtered, centrals_kfactor[0]
                )
        else:
            # In this case this means that the missing entries will multiply zero subgrids so we can just add 0s
            for _num in range(pigrid.bins()):
                centrals_kfactor_filtered = np.append(centrals_kfactor_filtered, 0.0)
    return centrals_kfactor_filtered


def compute_k_factor_grid(
    grids_folder,
    kfactor_folder,
    yamldb_path,
    max_as,
    target_folder=None,
    order_exists=False,
):
    """Include the k-factor in the grid in order to have its associated order in the grid itself.

    Parameters
    ----------
    grids_folder : pathlib.Path()
        pineappl grids folder
    kfactor_folder : pathlib.Path()
        kfactors folder
    yamldb_path : pathlib.Path()
        path to the yaml file describing the dataset
    max_as : int
        max as order
    target_folder: pathlib.Path
        path where store the new grid (optional)
    """
    import lhapdf  # pylint: disable=import-error

    # With respect to the usual convention here max_as is max_as-1
    max_as_test = max_as - 1
    # Extracting info from yaml file
    with open(yamldb_path, encoding="utf-8") as f:
        yamldict = yaml.safe_load(f)
    for grid_list in yamldict["operands"]:
        for grid in grid_list:
            cfac_path = kfactor_folder / f"CF_QCD_{grid}.dat"
            if "ATLASDY2D8TEV" in grid:
                cfac_path = kfactor_folder / f"CF_QCDEWK_{grid}.dat"
            centrals_kfactor, pdf_set = read_kfactor(cfac_path)
            alphas = lhapdf.mkAlphaS(pdf_set)
            grid_path = grids_folder / (f"{grid}.pineappl.lz4")
            pigrid = pineappl.grid.Grid.read(grid_path)
            centrals_kfactor_filtered = filter_k_factors(pigrid, centrals_kfactor)
            do_it(
                centrals_kfactor_filtered,
                alphas,
                grid_path,
                pigrid,
                max_as,
                max_as_test,
                target_folder,
                order_exists,
            )

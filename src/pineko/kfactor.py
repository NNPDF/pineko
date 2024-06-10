"""Module to include QCD kfactors in grids."""

import io

import numpy as np
import pineappl
import rich
import yaml
from pineappl import import_only_subgrid

from . import configs, fonll, scale_variations, utils
from .scale_variations import orders_as_tuple

DEFAULT_PDF_SET = "NNPDF40_nnlo_as_01180"


def read_from_file(kfactor_path):
    """Read the kfactor and returns the central values and the pdfset used to compute it."""
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
        # If there is no PDF set in the kfactor, a default PDF set will be used
        # If the PDF set written in the file is not an actual lhapdf PDF, it will
        # raise an error.
        if len(pdf_set) == 0:
            pdf_set = DEFAULT_PDF_SET
    return central_value, pdf_set


def compute_scale_factor(
    order,
    order_to_update,
    mu2,
    central_kfactor,
    bin_index,
    alphas,
):
    """Compute the factor to be multiplied to the given the required order.

    Parameters
    ----------
    order : tuple(int)
        tuple of the order that has to be rescaled to get the final order
    order_to_update : tuple(int)
        order to update
    mu2: float
        energy scale squared of the bin
    central_kfactor: list(float)
        list of the centrals kfactors
    bin_index: int
        index of the bin
    alphas: lhapdf.AlphaS
        alpha_s object
    """
    alpha_val = alphas.alphasQ2(mu2)
    max_as = order_to_update[0]
    as_order = order[0]
    alpha_term = 1.0 / pow(alpha_val, max_as - as_order)
    k_term = central_kfactor[bin_index] - 1.0
    return k_term * alpha_term


def scale_subgrid(subgrid, scales_array):
    """Rescales the array contained in the subgrid using scales_array."""
    original_array = subgrid.to_array3()
    if len(original_array) != len(scales_array):
        raise ValueError("The original and the scales arrays have different shapes.")
    # construct subgrid
    scaled_array = []
    for scale_value, arr_to_scale in zip(scales_array, original_array):
        scaled_array_nest = []
        for arr in arr_to_scale:
            scaled_array_nest.append(list(arr * scale_value))
        scaled_array.append(scaled_array_nest)
    if len(scales_array) == 0:
        scaled_array = np.zeros(shape=(0, 0, 0), dtype=float)
    else:
        scaled_array = np.array(scaled_array, dtype=float)
    # get coordinates
    x1grid = subgrid.x1_grid()
    x2grid = subgrid.x2_grid()
    mu2_grid = [tuple([mu2.ren, mu2.fac]) for mu2 in subgrid.mu2_grid()]
    # assemble
    scaled_subgrid = import_only_subgrid.ImportOnlySubgridV2(
        scaled_array, mu2_grid, x1grid, x2grid
    )
    return scaled_subgrid


def is_already_in_no_logs(to_check, list_orders):
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


def construct_new_order(grid, order, order_to_update, central_kfactor, alphas):
    """Construct a scaled grid, with the given order.

    Parameters
    ----------
    grid : pineappl.grid
        loaded grid
    order : tuple
        current alpha_s order
    order_to_update: tuple
        alpha_s order to update
    central_kfactor : np.ndarray
        kfactors to apply
    alphas : lhapdf.AlphaS
        alphas
    """
    # extract the relevant order to rescale from the grid for each lumi and bin
    grid_orders = orders_as_tuple(grid)

    new_grid = scale_variations.initialize_new_grid(grid, order_to_update)
    original_order_index = grid_orders.index(order)

    for lumi_index in range(len(new_grid.channels())):
        for bin_index in range(grid.bins()):
            subgrid = grid.subgrid(original_order_index, bin_index, lumi_index)
            mu2_ren_grid = [mu2.ren for mu2 in subgrid.mu2_grid()]
            scales_array = [
                compute_scale_factor(
                    order,
                    order_to_update,
                    mu2,
                    central_kfactor,
                    bin_index,
                    alphas,
                )
                for mu2 in mu2_ren_grid
            ]
            scaled_subgrid = scale_subgrid(subgrid, scales_array)
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


def apply_to_grid(
    central_kfactor,
    alphas,
    grid,
    pto_to_update,
    target_grid_path,
    order_exists,
):
    """Apply the centrals_kfactor to the grid.

    Parameters
    ----------
    central_kfactor : np.ndarray
        kfactors to apply
    alphas : lhapdf.AlphaS
        alphas
    grid : pineappl.grid
        loaded grid
    pto_to_update : int
        perturbative order to update: 1 = LO, 2 = NLO ...
        no matter which power of alpha_s it is.
    target_grid_path: pathlib.Path
        path where store the new grid
    order_exists: bool
        True if the order to update is already present
    """
    grid_orders = orders_as_tuple(grid)

    # remove not necessary orders
    # NOTE: eventual QED kfactors are not supported
    order_mask = pineappl.grid.Order.create_mask(grid.orders(), pto_to_update, 0, True)
    grid_orders_filtered = list(np.array(grid_orders)[order_mask])
    grid_orders_filtered.sort(key=scale_variations.qcd)
    min_as = grid_orders_filtered[0][0]
    # TODO: this is always going to be 0, given the mask above ...
    min_al = grid_orders_filtered[0][1]

    # the actual alpha_s order to update
    order_to_update = pto_to_update + min_as - 1
    order_to_update = (order_to_update, min_al, 0, 0)

    # check if the order is already there
    is_in = is_already_in_no_logs(order_to_update, grid_orders_filtered)

    # Prevent summing orders incoherently
    if is_in and not order_exists:
        rich.print("[green] Success: Requested order already in the grid.")
        return
    if not is_in and order_exists:
        rich.print("[red] Abort: order exists is True but order not in the grid.")
        return

    # loop on all the order to update
    max_as = grid_orders_filtered[-1][0]
    orders_list = [(de, min_al, 0, 0) for de in range(min_as, max_as + 1)]
    # create an empty grid and add the rescaled order
    new_order_grid = None
    for i, as_order in enumerate(orders_list):
        order_grid = construct_new_order(
            grid, as_order, order_to_update, central_kfactor, alphas
        )
        if i == 0:
            new_order_grid = order_grid
        else:
            new_order_grid.merge(order_grid)

    new_grid = grid
    # if the new order is there, clean the old one.
    if is_in:
        new_grid = scale_variations.construct_and_dump_order_exists_grid(
            grid, order_to_update
        )
    # merge the updated order with the original one.
    new_grid.merge(new_order_grid)
    new_grid.write_lz4(target_grid_path)


def to_list(grid, central_kfactors):
    """Cast the centrals kfactors to the correct length.

    Apply a normalization according to the length compared to the number of bins of the grid.

    Parameters
    ----------
    grid: pineappl.grid.Grid
        grid
    centrals_kfactor: list
        list of kfactor for each point
    """
    if grid.bins() == len(central_kfactors):
        rich.print("The number of bins match the length of the kfactor.")
        return central_kfactors
    if grid.bins() < len(central_kfactors):
        rich.print(
            "[yellow] The number of bins is less than the length of the kfactor."
        )
        if not len(np.unique(central_kfactors)) == 1:
            # This case is actually wrong.
            raise ValueError("kfactor contains too many different values.")
        return central_kfactors

    rich.print("[yellow] The number of bins is more than the length of the kfactor.")

    # This is the last case in which grid.bins() > len(centrals_kfactor)
    # Note that sometimes there are more bins in the grid than in the kfactor file -
    # this is not a problem because in those cases either all kfactor values are the
    # same (thus there is no doubt about whether we have the correct one) or the
    # non-existing kfactor would be multiplied by bins corresponding to all '0' in the
    # grid.
    # Let's check if we are in the first or second case
    if len(np.unique(central_kfactors)) == 1:
        # In this case I just need to add more elements to the kfactor
        return np.full(grid.bins(), central_kfactors[0])
    # In this case this means that the missing entries will
    # multiply zero subgrids so we can just add 0s
    return np.full(grid.bins(), 0)


def apply_to_dataset(
    theoryid,
    dataset,
    kfactor_folder,
    pto_to_update,
    target_folder,
    order_exists=False,
):
    """Include the kfactor in the grid in order to have its associated order in the grid itself.

    Parameters
    ----------
    theoryid : int
        theory ID of the source grid
    dataset : str
        datset name
    kfactor_folder : pathlib.Path()
        kfactors folder
    pto_to_update : int
        perturbative order to update: 1 = LO, 2 = NLO ...
        no matter which power of alpha_s it is.
    target_folder: pathlib.Path
        path where store the new grid
    order_exists: bool
        True if the order to update is already present
    """
    import lhapdf  # pylint: disable=import-error,import-outside-toplevel

    # Extracting info from yaml file
    grid_list = utils.read_grids_from_nnpdf(dataset, configs.configs)
    if grid_list is None:
        grid_list = fonll.grids_names(
            configs.configs["paths"]["ymldb"] / f"{dataset}.yaml"
        )

    # loop on grids_name
    for grid in grid_list:
        # TODO: generalize for other type of kfactors ?
        grid_name = grid.split(".")[0]
        kfactor_path = kfactor_folder / f"CF_QCD_{grid_name}.dat"
        if "ATLASDY2D8TEV" in grid:
            kfactor_path = kfactor_folder / f"CF_QCDEWK_{grid_name}.dat"

        current_grid = pineappl.grid.Grid.read(
            configs.configs["paths"]["grids"] / str(theoryid) / grid
        )

        central_kfactor, pdf_set = read_from_file(kfactor_path)
        central_kfactor_filtered = to_list(current_grid, central_kfactor)
        alphas = lhapdf.mkAlphaS(pdf_set)

        apply_to_grid(
            central_kfactor_filtered,
            alphas,
            current_grid,
            pto_to_update,
            target_folder / grid,
            order_exists,
        )

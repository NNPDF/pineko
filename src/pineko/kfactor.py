"""Module to include QCD K-factors in grids."""
import io
import pathlib

import numpy as np
import pineappl
import rich
import yaml

from . import scale_variations

DEFAULT_PDF_SET = "NNPDF40_nnlo_as_01180"


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
        if len(pdf_set) == 0:
            pdf_set = DEFAULT_PDF_SET
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
    new_grid = scale_variations.initialize_new_grid(grid, new_order)
    new_order_tuple = [ord.as_tuple() for ord in new_order]
    # extract the relevant order to rescale from the grid for each lumi and bin
    grid_orders = [order.as_tuple() for order in grid.orders()]
    order_index = grid_orders.index(order)
    for lumi_index in range(len(new_grid.lumi())):
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
    for order in list_orders:
        if (
            order[-2] == 0
            and order[-1] == 0
            and (order[0] == to_check[0])
            and (order[1] == to_check[1])
        ):
            return True
    return False


def get_bin_infos_and_grids(list_grids, grids_folder):
    """Get all the bin infos of the grids and return both the bins list and the loaded grids."""
    loaded_grid_list = []
    bins_list = []
    last_pos = 0
    for grid_name in list_grids:
        grid_path = grids_folder / (f"{grid_name}.pineappl.lz4")
        grid = pineappl.grid.Grid.read(grid_path)
        loaded_grid_list.append(grid)
        bins_list.append((last_pos, grid.bins() + last_pos))
        last_pos += grid.bins()
    return bins_list, loaded_grid_list


def construct_and_merge_grids(
    grid_path,
    max_as,
    first_nonzero_order,
    min_al,
    centrals_kfactor,
    alphas,
    target_folder,
):
    """Create, write and merge all the grids."""
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


def do_it(
    centrals_kfactor, alphas, grid_path, grid, max_as, max_as_test, target_folder
):
    """Apply the centrals_kfactor to the grid if the order is not already there."""
    grid_orders = [orde.as_tuple() for orde in grid.orders()]
    order_mask = pineappl.grid.Order.create_mask(grid.orders(), max_as, 0)
    grid_orders_filtered = list(np.array(grid_orders)[order_mask])
    grid_orders_filtered.sort(key=scale_variations.sort_qcd_orders)
    first_nonzero_order = grid_orders_filtered[0]
    min_al = first_nonzero_order[1]
    if is_already_in(
        (first_nonzero_order[0] + max_as_test, min_al, 0, 0), grid_orders_filtered
    ):
        rich.print(f"[green] Success: Requested order already in the grid.")
        return
    construct_and_merge_grids(
        grid_path,
        max_as_test,
        first_nonzero_order,
        min_al,
        centrals_kfactor,
        alphas,
        target_folder,
    )


def create_lists_for_compound(cfac_paths, list_grids, target_dataset, bins_list):
    """Given the Kfactors paths, the list of the grids associated to them, the name of the dataset and the list of the bins of the grids, construct the centrals kfactor and alphas object."""
    import lhapdf  # pylint: disable=import-error

    centrals_list = []
    alphas_list = []
    if len(cfac_paths) == len(list_grids):
        # Reading the k-factor
        for cfac_path in cfac_paths:
            if not cfac_path.exists():
                rich.print(f"[Red] Error: KFactor does not exist.")
                continue
            centrals_kfactor, pdf_set = read_kfactor(cfac_path)
            # Removing 1.0 entries only for "ATLASZPT8TEVMDIST"
            if target_dataset == "ATLASZPT8TEVMDIST":
                centrals_kfactor = centrals_kfactor[np.where(centrals_kfactor != 1)]
            # We need the pdf set to get the correct alpha values
            alphas = lhapdf.mkAlphaS(pdf_set)
            centrals_list.append(centrals_kfactor)
            alphas_list.append(alphas)
    # If there is only one Kfactor, this means that it contains all the factors for all the bins across all the grids.
    elif len(cfac_paths) == 1:
        if not cfac_paths[0].exists():
            raise ValueError("KFactor does not exist.")
        centrals_kfactor, pdf_set = read_kfactor(cfac_paths[0])
        # Removing 1.0 entries only for "ATLASZPT8TEVMDIST"
        if target_dataset == "ATLASZPT8TEVMDIST":
            centrals_kfactor = centrals_kfactor[np.where(centrals_kfactor != 1)]
        alphas = lhapdf.mkAlphaS(pdf_set)
        # alpha is trivial: it is always the same
        alphas_list = [alphas for _ in list_grids]
        # Here I need to use the bin infos
        centrals_list = [
            centrals_kfactor[bin_limit[0] : bin_limit[1]] for bin_limit in bins_list
        ]

    else:
        raise ValueError(
            "Number of kfactors does not match the number of grids and is not one."
        )
    return (centrals_list, alphas_list)


def compute_k_factor_grid(
    grids_folder,
    kfactor_folder,
    yamldb_path,
    compound_folder,
    max_as,
    target_folder=None,
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
    compound_folder : pathlib.Path()
        path to the compound folder
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
    target_dataset = yamldict["target_dataset"]
    operation = yamldict["operation"]
    compound_path = pathlib.Path(compound_folder) / f"FK_{target_dataset}-COMPOUND.dat"
    is_concatenated = False
    list_grids = []
    # For RATIO dataset the thing is a bit more messy
    if operation == "RATIO":
        is_concatenated = True
        for op_list in yamldict["operands"]:
            list_op_list = []
            for op in op_list:
                list_op_list.append(op)
            list_grids.append(list_op_list)
    else:
        for op in yamldict["operands"][0]:
            list_grids.append(op)
        if len(list_grids) > 1:
            is_concatenated = True

    # Simple case: dataset is not concatenated
    if not is_concatenated:
        if compound_path.exists():
            cfac_names = [
                i[3:-4] for i in compound_path.read_text().split() if i.endswith(".dat")
            ]
            cfac_paths = [kfactor_folder / f"CF_QCD_{i}.dat" for i in cfac_names]
        else:
            cfac_paths = [kfactor_folder / f"CF_QCD_{target_dataset}.dat"]
        if not cfac_paths[0].exists():
            raise ValueError("KFactor does not exist.")
        centrals_kfactor, pdf_set = read_kfactor(cfac_paths[0])
        alphas = lhapdf.mkAlphaS(pdf_set)
        grid_path = grids_folder / (f"{list_grids[0]}.pineappl.lz4")
        grid = pineappl.grid.Grid.read(grid_path)
        do_it(
            centrals_kfactor,
            alphas,
            grid_path,
            grid,
            max_as,
            max_as_test,
            target_folder,
        )
    else:
        if operation == "RATIO":
            # In this case we need to get the proper kfactors for numerator and denominator
            bins_list_num, loaded_grid_list_num = get_bin_infos_and_grids(
                list_grids[0], grids_folder
            )
            bins_list_den, loaded_grid_list_den = get_bin_infos_and_grids(
                list_grids[1], grids_folder
            )
            if compound_path.exists():
                cfac_names = [
                    i[3:-4]
                    for i in compound_path.read_text().split()
                    if i.endswith(".dat")
                ]
                cfac_names_num = [name for name in cfac_names if ("NUM" in name)]
                cfac_names_den = [name for name in cfac_names if ("DEN" in name)]
                # Sometimes they are not denoted with NUM and DEN
                if target_dataset in [
                    "ATLAS_SINGLETOP_TCH_R_8TEV",
                    "ATLAS_SINGLETOP_TCH_R_7TEV",
                    "ATLAS_SINGLETOP_TCH_R_13TEV",
                    "CMS_SINGLETOP_TCH_R_13TEV",
                    "CMS_SINGLETOP_TCH_R_8TEV",
                ]:
                    cfac_names_num = [target_dataset + "_T"]
                    cfac_names_den = [target_dataset + "_TB"]
                if target_dataset == "D0ZRAP":
                    cfac_names_num = [target_dataset]
                    cfac_names_den = [target_dataset + "_TOT"]
                cfac_paths_num = [
                    kfactor_folder / f"CF_QCD_{i}.dat" for i in cfac_names_num
                ]
                cfac_paths_den = [
                    kfactor_folder / f"CF_QCD_{i}.dat" for i in cfac_names_den
                ]
            else:
                raise ValueError(
                    "Operation is RATIO but no compound file has been found."
                )
            centrals_list_num, alphas_list_num = create_lists_for_compound(
                cfac_paths_num, list_grids[0], target_dataset, bins_list_num
            )
            centrals_list_den, alphas_list_den = create_lists_for_compound(
                cfac_paths_den, list_grids[1], target_dataset, bins_list_den
            )
            # Flattening and concatenating all the lists
            loaded_grid_list = list(
                np.concatenate((loaded_grid_list_num, loaded_grid_list_den))
            )
            for grid_el, cen_el, alpha_el in zip(
                list_grids[1], centrals_list_den, alphas_list_den
            ):
                list_grids[0].append(grid_el)
                centrals_list_num.append(cen_el)
                alphas_list_num.append(alpha_el)
            list_grids = list_grids[0]
            centrals_list = centrals_list_num
            alphas_list = alphas_list_num
        else:
            # In this case is convenient to load all the grids now and store the bin info
            bins_list, loaded_grid_list = get_bin_infos_and_grids(
                list_grids, grids_folder
            )
            # if compound file exists, take cfactor file names from there.
            # If not then the cfactor file name can be obtained form the target dataset name alone.
            if compound_path.exists():
                cfac_names = [
                    i[3:-4]
                    for i in compound_path.read_text().split()
                    if i.endswith(".dat")
                ]
                cfac_paths = [kfactor_folder / f"CF_QCD_{i}.dat" for i in cfac_names]
            else:
                cfac_paths = [kfactor_folder / f"CF_QCD_{target_dataset}.dat"]
            # I need to check how many Kfactors I have
            centrals_list, alphas_list = create_lists_for_compound(
                cfac_paths, list_grids, target_dataset, bins_list
            )

        # Now we are ready to do the magic for each grid
        for grid_name, grid, centrals_cfac, alpha in zip(
            list_grids, loaded_grid_list, centrals_list, alphas_list
        ):
            grid_path = grids_folder / (f"{grid_name}.pineappl.lz4")
            # We need to check if the number of factors in the Kfactors match the number of bin
            # If not we need to do different things according to the problem
            # This is the easy case
            if grid.bins() == len(centrals_cfac):
                rich.print(
                    f"[orange] The number of bins match the lenght of the kFactor."
                )
            elif grid.bins() < len(centrals_cfac):
                rich.print(
                    f"[yellow] The number of bins is less than the lenght of the kFactor."
                )
                if not all(elem == centrals_cfac[0] for elem in centrals_cfac):
                    # This case is actually wrong.
                    raise ValueError("KFactor contains too many different values.")
            else:
                rich.print(
                    f"[yellow] The number of bins is more than the lenght of the KFactor."
                )

                # This is the last case in which grid.bins() > len(centrals_kfactor)

                # Note that sometimes there are more bins in the grid than in the cfactor file -
                # this is not a problem becasue in those cases either all cfactor values are the
                # same (thus there is no doubt about whether we have the correct one) or the
                # non-exisiting cfactors would be multiplied by bins corresponding to all '0' in the
                # grid.
                # Let's check if we are in the first or second case
                if len(np.unique(centrals_cfac)) == 1:
                    # In this case I just need to add more elements to the kfactor
                    for _num in range(grid.bins() - len(centrals_cfac)):
                        centrals_cfac = np.append(centrals_cfac, centrals_cfac[0])
                else:
                    # In this case this means that the missing entries will multiply zero subgrids so we can just add 0s
                    for _num in range(grid.bins() - len(centrals_cfac)):
                        centrals_cfac = np.append(centrals_cfac, 0.0)
            do_it(
                centrals_cfac,
                alpha,
                grid_path,
                grid,
                max_as,
                max_as_test,
                target_folder,
            )

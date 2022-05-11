# -*- coding: utf-8 -*-
import copy
import pathlib

import eko
import eko.basis_rotation as br
import numpy as np
import pineappl
import rich
import rich.box
import rich.panel
import yaml

from . import check, comparator


def write_operator_card_from_file(pineappl_path, default_card_path, card_path):
    """Generate operator card for a grid.

    Parameters
    ----------
    pineappl_path : str or os.PathLike
        path to grid to evolve
    default_card : str or os.PathLike
        base operator card
    card_path : str or os.PathLike
        target path

    Returns
    -------
    x_grid : np.ndarray
        written x grid
    q2_grid : np.ndarray
        written Q2 grid
    """
    # raise in python rather then rust
    if not pathlib.Path(pineappl_path).exists():
        raise FileNotFoundError(pineappl_path)
    pineappl_grid = pineappl.grid.Grid.read(pineappl_path)
    with open(default_card_path, "r", encoding="UTF-8") as f:
        default_card = yaml.safe_load(f)
    return write_operator_card(pineappl_grid, default_card, card_path)


def write_operator_card(pineappl_grid, default_card, card_path):
    """Generate operator card for this grid.

    Parameters
    ----------
    pineappl_grid : pineappl.grid.Grid
        grid to evolve
    default_card : dict
        base operator card
    card_path : str or os.PathLike
        target path

    Returns
    -------
    x_grid : np.ndarray
        written x grid
    q2_grid : np.ndarray
        written Q2 grid
    """
    operators_card = copy.deepcopy(default_card)
    x_grid, _pids, q2_grid = pineappl_grid.axes()
    operators_card["targetgrid"] = x_grid.tolist()
    operators_card["Q2grid"] = q2_grid.tolist()
    with open(card_path, "w", encoding="UTF-8") as f:
        yaml.safe_dump(operators_card, f)
    return x_grid, q2_grid


def evolve_grid(
    pineappl_path, eko_path, fktable_path, max_as, max_al, xir, xif, comparison_pdf=None
):
    """
    Convolute grid with EKO from file paths.

    Parameters
    ----------
        pineappl_path : str
            unconvoluted grid
        eko_path : str
            evolution operator
        fktable_path : str
            target path for convoluted grid
        max_as : int
            maximum power of strong coupling
        max_al : int
            maximum power of electro-weak coupling
        xir : float
            renormalization scale variation
        xif : float
            factorization scale variation
        comparison_pdf : None or str
            if given, a comparison table (with / without evolution) will be printed
    """
    rich.print(
        rich.panel.Panel.fit("Computing ...", style="magenta", box=rich.box.SQUARE),
        f"   {pineappl_path}\n",
        f"+ {eko_path}\n",
        f"= {fktable_path}\n",
        f"with max_as={max_as}, max_al={max_al}, xir={xir}, xif={xif}"
    )
    # load
    pineappl_grid = pineappl.grid.Grid.read(str(pineappl_path))
    operators = eko.output.Output.load_tar(eko_path)
    check.check_grid_and_eko_compatible(pineappl_grid, operators)
    # rotate to evolution (if doable and necessary)
    if np.allclose(operators["inputpids"], br.flavor_basis_pids):
        operators.to_evol()
    elif not np.allclose(operators["inputpids"], br.evol_basis_pids):
        raise ValueError("The EKO is neither in flavor nor in evolution basis.")
    # do it
    order_mask = pineappl.grid.Order.create_mask(pineappl_grid.orders(), max_as, max_al)
    # TODO this is a hack to not break the CLI
    # the problem is that the EKO output still does not contain the theory/operators card and
    # so I can't compute alpha_s here if xir != 1
    if np.isclose(xir, 1.):
        mur2_grid = list(operators["Q2grid"].keys())
        alphas_values = [op["alphas"] for op in operators["Q2grid"].values()]
    fktable = pineappl_grid.convolute_eko(operators, mur2_grid, alphas_values, "evol", order_mask=order_mask,xi=(xir, xif))
    fktable.optimize()
    # compare before after
    comparison = None
    if comparison_pdf is not None:
        comparison = comparator.compare(
                pineappl_grid, fktable, max_as, max_al, comparison_pdf
            )
        fktable.set_key_value("results_fk", comparison.to_string())
        fktable.set_key_value("results_fk_pdfset", comparison_pdf)
    # write
    fktable.write_lz4(str(fktable_path))
    return pineappl_grid, fktable, comparison

# -*- coding: utf-8 -*-
"""Tools related to evolution/eko."""
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


def write_operator_card_from_file(pineappl_path, default_card_path, card_path, xif):
    """Generate operator card for a grid.

    Parameters
    ----------
    pineappl_path : str or os.PathLike
        path to grid to evolve
    default_card : str or os.PathLike
        base operator card
    card_path : str or os.PathLike
        target path
    xif : float
        factorization scale variation

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
    return write_operator_card(pineappl_grid, default_card, card_path, xif)


def write_operator_card(pineappl_grid, default_card, card_path, xif):
    """Generate operator card for this grid.

    Parameters
    ----------
    pineappl_grid : pineappl.grid.Grid
        grid to evolve
    default_card : dict
        base operator card
    card_path : str or os.PathLike
        target path
    xif : float
        factorization scale variation

    Returns
    -------
    x_grid : np.ndarray
        written x grid
    q2_grid : np.ndarray
        written Q2 grid
    """
    operators_card = copy.deepcopy(default_card)
    x_grid, _pids, _mur2_grid, muf2_grid = pineappl_grid.axes()
    q2_grid = (xif * xif * muf2_grid).tolist()
    operators_card["targetgrid"] = x_grid.tolist()
    operators_card["Q2grid"] = q2_grid
    with open(card_path, "w", encoding="UTF-8") as f:
        yaml.safe_dump(operators_card, f)
    return x_grid, q2_grid


def evolve_grid(
    grid,
    operators,
    fktable_path,
    max_as,
    max_al,
    xir,
    xif,
    alphas_values=None,
    assumptions="Nf6Ind",
    comparison_pdf=None,
):
    """Convolute grid with EKO from file paths.

    Parameters
    ----------
    grid : pineappl.grid.Grid
        unconvoluted grid
    operators : eko.output.Output
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
    alphas_values : None or list
        values of strong coupling used to collapse grids
    assumptions : str
        assumptions on the flavor dimension
    comparison_pdf : None or str
        if given, a comparison table (with / without evolution) will be printed
    """
    _x_grid, _pids, mur2_grid, _muf2_grid = grid.axes()
    check.check_grid_and_eko_compatible(grid, operators, xif)
    # rotate to evolution (if doable and necessary)
    if np.allclose(operators["inputpids"], br.flavor_basis_pids):
        operators.to_evol()
    elif not np.allclose(operators["inputpids"], br.evol_basis_pids):
        raise ValueError("The EKO is neither in flavor nor in evolution basis.")
    # do it
    order_mask = pineappl.grid.Order.create_mask(grid.orders(), max_as, max_al)
    # TODO this is a hack to not break the CLI
    # the problem is that the EKO output still does not contain the theory/operators card and
    # so I can't compute alpha_s *here* if xir != 1
    if np.isclose(xir, 1.0) and alphas_values is None:
        mur2_grid = list(operators["Q2grid"].keys())
        alphas_values = [op["alphas"] for op in operators["Q2grid"].values()]
    fktable = grid.convolute_eko(
        operators,
        xir * xir * mur2_grid,
        alphas_values,
        "evol",
        order_mask=order_mask,
        xi=(xir, xif),
    )
    rich.print(f"Optimizing for {assumptions}")
    fktable.optimize(assumptions)
    # write
    fktable.write_lz4(str(fktable_path))
    # compare before/after
    comparison = None
    if comparison_pdf is not None:
        comparison = comparator.compare(
            grid, fktable, max_as, max_al, comparison_pdf, xir, xif
        )
        fktable.set_key_value("results_fk", comparison.to_string())
        fktable.set_key_value("results_fk_pdfset", comparison_pdf)
    return grid, fktable, comparison

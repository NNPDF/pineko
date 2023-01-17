"""Tools related to evolution/eko."""
import copy
import os
import pathlib

import eko
import eko.basis_rotation as br
import numpy as np
import pineappl
import rich
import rich.box
import rich.panel
import yaml

from . import check, comparator, ekompatibility, version


def write_operator_card_from_file(
    pineappl_path: os.PathLike,
    default_card_path: os.PathLike,
    card_path: os.PathLike,
    xif: float,
    tcard_path: os.PathLike,
):
    """Generate operator card for a grid.

    Note
    ----
    For the reason why `tcard` is required, see :func:`write_operator_card`.

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
    tcard_path: dict
        theory card for the run

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
    default_card = yaml.safe_load(
        pathlib.Path(default_card_path).read_text(encoding="utf-8")
    )
    tcard = yaml.safe_load(pathlib.Path(tcard_path).read_text(encoding="utf-8"))
    return write_operator_card(pineappl_grid, default_card, card_path, xif, tcard)


def write_operator_card(pineappl_grid, default_card, card_path, xif, tcard):
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
    tcard: dict
        theory card for the run, since some information in EKO is now required
        in operator card, but before was in the theory card

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
    operators_card["rotations"]["_targetgrid"] = x_grid.tolist()
    operators_card["_mugrid"] = np.sqrt(q2_grid).tolist()
    if not np.isclose(xif, 1.0):
        operator_card["configs"]["scvar_method"] = "expanded"
    if "integrability_version" in pineappl_grid.key_values():
        operators_card["configs"]["interpolation_polynomial_degree"] = 1
        x_grid_int = copy.deepcopy(x_grid.tolist())
        x_grid_int.append(1.0)
        operators_card["rotations"]["_targetgrid"] = list(x_grid_int)

    with open(card_path, "w", encoding="UTF-8") as f:
        yaml.safe_dump(operators_card, f)
    return x_grid, q2_grid


def evolve_grid(
    grid,
    operators,
    fktable_path,
    sc,
    max_as,
    max_al,
    xir,
    xif,
    assumptions="Nf6Ind",
    comparison_pdf=None,
):
    """Convolute grid with EKO from file paths.

    Parameters
    ----------
    grid : pineappl.grid.Grid
        unconvoluted grid
    operators : eko.EKO
        evolution operator
    fktable_path : str
        target path for convoluted grid
    sc : eko.coupling.Couplings
        couplings object
    max_as : int
        maximum power of strong coupling
    max_al : int
        maximum power of electro-weak coupling
    xir : float
        renormalization scale variation
    xif : float
        factorization scale variation
    assumptions : str
        assumptions on the flavor dimension
    comparison_pdf : None or str
        if given, a comparison table (with / without evolution) will be printed
    """
    _x_grid, _pids, mur2_grid, _muf2_grid = grid.axes()
    check.check_grid_and_eko_compatible(grid, operators, xif)
    # rotate to evolution (if doable and necessary)
    if np.allclose(operators.rotations.inputpids, br.flavor_basis_pids):
        eko.io.manipulate.to_evol(operators)
    elif not np.allclose(operators.rotations.inputpids, br.evol_basis_pids):
        raise ValueError("The EKO is neither in flavor nor in evolution basis.")
    # do it
    order_mask = pineappl.grid.Order.create_mask(grid.orders(), max_as, max_al)
    muf2_grid = operators.mu2grid
    # PineAPPL wants alpha_s = 4*pi*a_s
    # remember that we already accounted for xif in the opcard generation
    alphas_values = [
        4.0 * np.pi * sc.a_s(xir * xir * muf2 / xif / xif, fact_scale=muf2)
        for muf2 in muf2_grid
    ]
    fktable = grid.evolve(
        ekompatibility.pineappl_layout(operators),
        xir * xir * mur2_grid,
        alphas_values,
        "evol",
        order_mask=order_mask,
        xi=(xir, xif),
    )
    rich.print(f"Optimizing for {assumptions}")
    fktable.optimize(assumptions)
    fktable.set_key_value("eko_version", operators.metadata.version)
    fktable.set_key_value("pineko_version", version.__version__)
    # compare before/after
    comparison = None
    if comparison_pdf is not None:
        comparison = comparator.compare(
            grid, fktable, max_as, max_al, comparison_pdf, xir, xif
        )
        fktable.set_key_value("results_fk", comparison.to_string())
        fktable.set_key_value("results_fk_pdfset", comparison_pdf)
    # write
    fktable.write_lz4(str(fktable_path))
    return grid, fktable, comparison

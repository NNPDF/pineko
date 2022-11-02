"""Tools related to evolution/eko."""
import copy
import os
import pathlib

import eko
import eko.basis_rotation as br
import eko.compatibility
import numpy as np
import pineappl
import rich
import rich.box
import rich.panel
import yaml

from . import check, comparator, ekompatibility, version

DEFAULT_PIDS = [-5, -4, -3, -2, -1, 21, 22, 1, 2, 3, 4, 5]


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
    operators_card["targetgrid"] = x_grid.tolist()
    operators_card["Q2grid"] = q2_grid
    if "integrability_version" in pineappl_grid.key_values():
        operators_card["interpolation_polynomial_degree"] = 1
        x_grid_int = copy.deepcopy(x_grid.tolist())
        x_grid_int.append(1.0)
        operators_card["interpolation_xgrid"] = list(x_grid_int)

    def provide_if_missing(key, default, card=operators_card):
        if key not in card:
            card[key] = default

    provide_if_missing("n_integration_cores", 1)
    provide_if_missing("inputgrid", operators_card["interpolation_xgrid"])
    provide_if_missing("targetgrid", operators_card["interpolation_xgrid"])
    provide_if_missing("inputpids", DEFAULT_PIDS)
    provide_if_missing("targetpids", DEFAULT_PIDS)

    _, new_operators_card = eko.compatibility.update(tcard, operators_card)
    with open(card_path, "w", encoding="UTF-8") as f:
        yaml.safe_dump(new_operators_card, f)
    return x_grid, q2_grid


def evolve_grid(
    grid,
    operators,
    fktable_path,
    astrong,
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
    operators : eko.output.struct.EKO
        evolution operator
    fktable_path : str
        target path for convoluted grid
    astrong : eko.coupling.Couplings
        as object
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
    if np.allclose(operators.rotations.pids, br.flavor_basis_pids):
        eko.output.manipulate.to_evol(operators)
    elif not np.allclose(operators.rotations.inputpids, br.evol_basis_pids):
        raise ValueError("The EKO is neither in flavor nor in evolution basis.")
    # do it
    order_mask = pineappl.grid.Order.create_mask(grid.orders(), max_as, max_al)
    # TODO this is a hack to not break the CLI
    # the problem is that the EKO output still does not contain the theory/operators card and
    # so I can't compute alpha_s *here* if xir != 1
    if np.isclose(xir, 1.0) and alphas_values is None:
        mur2_grid = np.array(list(operators.Q2grid))
        alphas_values = [astrong.a_s(q2) for q2 in operators.Q2grid]
    fktable = grid.convolute_eko(
        ekompatibility.pineappl_layout(operators),
        xir * xir * mur2_grid,
        alphas_values,
        "evol",
        order_mask=order_mask,
        xi=(xir, xif),
    )
    rich.print(f"Optimizing for {assumptions}")
    fktable.optimize(assumptions)
    fktable.set_key_value("eko_version", operators.version)
    fktable.set_key_value("pineko_version", version.__version__)
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

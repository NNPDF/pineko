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
from eko.io.types import ScaleVariationsMethod
from eko.matchings import Atlas, nf_default
from eko.quantities import heavy_quarks

from . import check, comparator, ekompatibility, version


def sv_scheme(tcard):
    """Infere the factorization scale_variation scheme to be used from the theory card.

    Parameters
    ----------
    tcard : dict
        theory card

    """
    modsv_list = {a.value for a in ScaleVariationsMethod}
    xif = tcard["XIF"]
    modsv = tcard["ModSV"]
    if np.isclose(xif, 1.0):
        if modsv in modsv_list:
            raise ValueError("ModSv is not None but xif is 1.0")
        return None
    # scheme C case
    if modsv not in modsv_list:
        return None
    return modsv


def write_operator_card_from_file(
    pineappl_path: os.PathLike,
    default_card_path: os.PathLike,
    card_path: os.PathLike,
    tcard,
):
    """Generate operator card for a grid.

    Parameters
    ----------
    pineappl_path : str or os.PathLike
        path to grid to evolve
    default_card : str or os.PathLike
        base operator card
    card_path : str or os.PathLike
        target path
    tcard: dict
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
    return write_operator_card(pineappl_grid, default_card, card_path, tcard)


def write_operator_card(pineappl_grid, default_card, card_path, tcard):
    """Generate operator card for this grid.

    Parameters
    ----------
    pineappl_grid : pineappl.grid.Grid
        grid to evolve
    default_card : dict
        base operator card
    card_path : str or os.PathLike
        target path
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
    # Add a +1 to the orders for the difference in convention between nnpdf and pineappl
    is_fns = int(check.is_fonll_b(tcard["FNS"], pineappl_grid.lumi()))
    max_as = 1 + tcard["PTO"] + is_fns
    max_al = 1 + tcard["QED"]
    # ... in order to create a mask ...
    order_mask = pineappl.grid.Order.create_mask(
        pineappl_grid.orders(), max_as, max_al, True
    )
    # ... to get the x and muF grids for the eko
    evol_info = pineappl_grid.evolve_info(order_mask)
    muf2_grid = evol_info.fac1
    operators_card = copy.deepcopy(default_card)
    sv_method = sv_scheme(tcard)
    xif = 1.0 if sv_method is not None else tcard["XIF"]
    operators_card["configs"]["scvar_method"] = sv_method
    q2_grid = (xif * xif * muf2_grid).tolist()
    masses = np.array([tcard["mc"], tcard["mb"], tcard["mt"]]) ** 2
    thresholds_ratios = np.array([tcard["kcThr"], tcard["kbThr"], tcard["ktThr"]]) ** 2
    for q in range(tcard["MaxNfPdf"] + 1, 6 + 1):
        thresholds_ratios[q - 4] = np.inf
    atlas = Atlas(
        matching_scales=heavy_quarks.MatchingScales(masses * thresholds_ratios),
        origin=(tcard["Q0"] ** 2, tcard["nf0"]),
    )
    operators_card["mugrid"] = [
        (float(np.sqrt(q2)), int(nf_default(q2, atlas))) for q2 in q2_grid
    ]
    if "integrability_version" in pineappl_grid.key_values():
        x_grid = evol_info.x1
        x_grid = np.append(x_grid, 1.0)
        operators_card["configs"]["interpolation_polynomial_degree"] = 1
        operators_card["xgrid"] = x_grid.tolist()

    with open(card_path, "w", encoding="UTF-8") as f:
        yaml.safe_dump(operators_card, f)
    return operators_card["xgrid"], q2_grid


def evolve_grid(
    grid,
    operators,
    fktable_path,
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
    order_mask = pineappl.grid.Order.create_mask(grid.orders(), max_as, max_al, True)
    evol_info = grid.evolve_info(order_mask)
    x_grid = evol_info.x1
    mur2_grid = evol_info.ren1
    xif = 1.0 if operators.operator_card.configs.scvar_method is not None else xif
    tcard = operators.theory_card
    opcard = operators.operator_card
    # rotate the targetgrid
    if "integrability_version" in grid.key_values():
        x_grid = np.append(x_grid, 1.0)
    eko.io.manipulate.xgrid_reshape(
        operators, targetgrid=eko.interpolation.XGrid(x_grid)
    )
    check.check_grid_and_eko_compatible(grid, operators, xif, max_as, max_al)
    # rotate to evolution (if doable and necessary)
    if np.allclose(operators.bases.inputpids, br.flavor_basis_pids):
        eko.io.manipulate.to_evol(operators)
    # Here we are checking if the EKO contains the rotation matrix (flavor to evol)
    elif not np.allclose(operators.bases.inputpids, br.rotate_flavor_to_evolution):
        raise ValueError("The EKO is neither in flavor nor in evolution basis.")
    # PineAPPL wants alpha_s = 4*pi*a_s
    # remember that we already accounted for xif in the opcard generation
    evmod = eko.couplings.couplings_mod_ev(opcard.configs.evolution_method)
    # Couplings ask for the square of the masses
    thresholds_ratios = np.power(tcard.heavy.matching_ratios, 2.0)
    for q in range(tcard.couplings.max_num_flavs + 1, 6 + 1):
        thresholds_ratios[q - 4] = np.inf
    sc = eko.couplings.Couplings(
        tcard.couplings,
        tcard.order,
        evmod,
        masses=[(x.value) ** 2 for x in tcard.heavy.masses],
        hqm_scheme=tcard.heavy.masses_scheme,
        thresholds_ratios=thresholds_ratios.tolist(),
    )
    # To compute the alphas values we are first reverting the factorization scale shift
    # and then obtaining the renormalization scale using xir.
    alphas_values = [
        4.0
        * np.pi
        * sc.a_s(
            xir * xir * mur2,
        )
        for mur2 in mur2_grid
    ]
    # We need to use ekompatibility in order to pass a dictionary to pineappl
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

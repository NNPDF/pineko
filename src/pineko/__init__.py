import eko
import lz4
import numpy as np
import pineappl
import rich
import rich.box
import rich.panel
import eko.basis_rotation as br

from .comparator import compare


def in1d(a, b, rtol=1e-05, atol=1e-08):
    """
    Improved version of np.in1d.

    Thanks: https://github.com/numpy/numpy/issues/7784#issuecomment-848036186
    """
    if len(a) == 1:
        for be in b:
            if np.isclose(be, a[0], rtol=rtol, atol=atol):
                return [True]
        return [False]
    ss = np.searchsorted(a[1:-1], b, side="left")
    return np.isclose(a[ss], b, rtol=rtol, atol=atol) | np.isclose(
        a[ss + 1], b, rtol=rtol, atol=atol
    )


def check_grid_and_eko_compatible(pineappl_grid, operators):
    """
    Raises a `ValueError` if the EKO operators and the PineAPPL grid are NOT compatible.

    Parameters
    ----------
        pineappl_grid : pineappl.grid.Grid
            grid
        operators : eko.output.Output
            operators
    """
    x_grid, _pids, muf2_grid = pineappl_grid.axes()
    # Q2 grid
    if not np.all(
        in1d(np.unique(list(operators["Q2grid"].keys())), np.array(muf2_grid))
    ):
        raise ValueError(
            "Q2 grid in pineappl grid and eko operator are NOT compatible!"
        )
    # x-grid
    if not np.all(in1d(np.unique(operators["targetgrid"]), np.array(x_grid))):
        raise ValueError("x grid in pineappl grid and eko operator are NOT compatible!")


def order_finder(pine):
    """
    Returns masks for LO+QCD and EW.

    Parameters
    ----------
        pine : pineappl.grid.Grid
            PineAPPL grid

    Returns
    -------
        mask_qcd : list(bool)
            LO + QCD
        mask_ew : list(bool)
            EW
    """
    qcd = np.array([1, 0, 0, 0])
    ew = np.array([0, 1, 0, 0])
    orders = [np.array(orde.as_tuple()) for orde in pine.orders()]
    LO = orders[0]
    mask_qcd = [True] + [False] * (len(orders) - 1)
    mask_ew = [False] + [False] * (len(orders) - 1)
    for i, order in enumerate(orders):
        if np.allclose(order, LO + qcd):
            mask_qcd[i] = True
        if np.allclose(order, LO + ew):
            mask_ew[i] = True
    return mask_qcd, mask_ew


def convolute(pineappl_path, eko_path, fktable_path, comparison_pdf=None):
    """
    Invoke steps from file paths.

    Parameters
    ----------
        pineappl_path : str
            unconvoluted grid
        eko_path : str
            evolution operator
        fktable_path : str
            target path for convoluted grid
        comparison_pdf : None or str
            if given, a comparison table (with / without evolution) will be printed
    """
    rich.print(
        rich.panel.Panel.fit(f"Computing ...", style="magenta", box=rich.box.SQUARE),
        f"   {pineappl_path}\n",
        f"+ {eko_path}\n",
        f"= {fktable_path}",
    )
    # load
    pineappl_grid = pineappl.grid.Grid.read(str(pineappl_path))
    operators = eko.output.Output.load_tar(eko_path)
    check_grid_and_eko_compatible(pineappl_grid, operators)
    # rotate to evolution (if doable and necessary)
    if np.allclose(operators["inputpids"], br.flavor_basis_pids):
        operators.to_evol()
    elif not np.allclose(operators["inputpids"], br.evol_basis_pids):
        raise ValueError("The EKO is neither in flavor nor in evolution basis.")
    # do it
    order_mask_qcd, _ = order_finder(pineappl_grid)
    fktable = pineappl_grid.convolute_eko(operators, "evol", order_mask=order_mask_qcd)
    # write
    fktable.write_lz4(str(fktable_path))
    # compare before after
    if comparison_pdf is not None:
        print(compare(pineappl_grid, fktable, comparison_pdf).to_string())

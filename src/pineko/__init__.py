import eko
import numpy as np
import pineappl
import rich
import rich.box
import rich.panel
import eko.basis_rotation as br

from .comparator import compare

__version__ = "0.0.0"


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


def convolute(
    pineappl_path, eko_path, fktable_path, max_as, max_al, comparison_pdf=None
):
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
        max_as : int
            maximum power of strong coupling
        max_al : int
            maximum power of electro-weak coupling
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
    order_mask = pineappl.grid.Order.create_mask(pineappl_grid.orders(), max_as, max_al)
    fktable = pineappl_grid.convolute_eko(operators, "evol", order_mask=order_mask)
    # write
    fktable.write_lz4(str(fktable_path))
    # compare before after
    if comparison_pdf is not None:
        print(
            compare(pineappl_grid, fktable, max_as, max_al, comparison_pdf).to_string()
        )

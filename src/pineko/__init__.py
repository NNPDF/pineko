import eko
import numpy as np
import pineappl
import rich
import rich.box
import rich.panel
import eko.basis_rotation as br

from .comparator import compare


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
    x_grid, q2_grid = pineappl_grid.eko_info()
    # Q2 grid
    if not np.allclose(list(operators["Q2grid"].keys()), q2_grid):
        raise ValueError("Q2 grid in pineappl grid and eko operator are NOT the same!")
    # x-grid
    if not np.allclose(operators["interpolation_xgrid"], x_grid):
        raise ValueError("x grid in pineappl grid and eko operator are NOT the same!")


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
        f"  {pineappl_path}",
        f"\n+ {eko_path}",
        f"\n= {fktable_path}",
    )
    # load
    pineappl_grid = pineappl.grid.Grid.read(str(pineappl_path))
    operators = eko.output.Output.load_yaml_from_file(eko_path)
    check_grid_and_eko_compatible(pineappl_grid, operators)
    # rotate to evolution (if doable and necessary)
    if np.allclose(operators["inputpids"], br.flavor_basis_pids):
        operators.to_evol()
    elif not np.allclose(operators["inputpids"], br.evol_basis_pids):
        raise ValueError("The EKO is neither in flavor nor in evolution basis.")
    # do it
    fktable = pineappl_grid.convolute_eko(operators)
    # write
    fktable.write(str(fktable_path))
    # compare before after
    if comparison_pdf is not None:
        print(compare(pineappl_grid, fktable, comparison_pdf))

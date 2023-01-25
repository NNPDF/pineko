"""Module to generate scale variations."""
import pineappl
import rich
from eko import beta

from . import check


def construct_ren_sv_grid(grid, max_as, nf):
    """Generate renormalization scale variation terms for the given grid, according to the max_as.

    Parameters
    ----------
    grid : pineappl.grid.Grid
        pineappl grid
    max_as : int
        max as order
    nf : int
        number of active flavors
    """
    # First let's check if the ren_sv are already there
    sv_as, sv_al = check.contains_ren(grid, max_as, max_al=0)
    if sv_as:
        rich.print(f"[green]Renormalization scale variations are already in the grid")
    ### Extract the correct subgrid and call the function to scale it


def LO_ren_var(m, k_R, nf):
    """LO ren scale variations depending on the first non vanishing order m.

    k_R is defined as the log(mu_{R}^{2}/ Q^2).

    nf is the number of active flavors.
    """
    return 1.0


def NLO_ren_var(m, k_R, nf):
    """NLO ren scale variations depending on the first non vanishing order m.

    k_R is defined as the log(mu_{R}^{2}/ Q^2).

    nf is the number of active flavors.
    """
    return -k_R * m * beta.beta_qcd((2, 0), nf)


def NNLO_ren_var(m, k_R, nf):
    """NNLO ren scale variations depending on the first non vanishing order m.

    k_R is defined as the log(mu_{R}^{2}/ Q^2).

    nf is the number of active flavors.
    """
    lo_logpiece = m * beta.beta_qcd((3, 0), nf)
    lo_log2piece = 0.5 * m * (m + 1) * (beta.beta_qcd((2, 0), nf) ** 2)
    locoeff = -k_R * lo_logpiece + (k_R**2) * lo_log2piece
    nlo_logpiece = (m + 1) * beta.beta_qcd((2, 0), nf)
    nlocoeff = -k_R * nlo_logpiece
    return (locoeff, nlocoeff)

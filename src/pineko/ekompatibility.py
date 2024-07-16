"""Compatibility layer for EKO migration."""

from eko import EKO, basis_rotation
from pineappl.grid import PyOperatorSliceInfo, PyPidBasis


def pineappl_layout(operator: EKO) -> list:
    """Extract information required by :func:`pineappl.grid.Grid.convolve_eko`.

    Parameters
    ----------
    operator: eko.EKO
        evolution operator in the new layout

    Returns
    -------
    dict
        a minimal object, with all and only the information consumed by PineAPPL

    """
    eko_iterator = []
    for (q2, _), op in operator.items():
        info = PyOperatorSliceInfo(
            fac0=operator.mu20,
            x0=operator.bases.inputgrid.raw,
            pids0=basis_rotation.evol_basis_pids,
            fac1=q2,
            x1=operator.bases.targetgrid.raw,
            pids1=operator.bases.targetpids,
            pid_basis=PyPidBasis.Pdg,
        )
        eko_iterator.append((info, op.operator))
    return eko_iterator

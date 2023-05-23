"""Compatibility layer for EKO migration."""
from typing import Any, Dict

from eko import EKO, basis_rotation


def pineappl_layout(operator: EKO) -> Dict[str, Any]:
    """Extract information required by :func:`pineappl.grid.Grid.convolute_eko`.

    Parameters
    ----------
    operator: eko.EKO
        evolution operator in the new layout

    Returns
    -------
    dict
        a minimal object, with all and only the information consumed by PineAPPL

    """
    oldgrid = {}
    oldgrid["Q2grid"] = {}
    for q2, op in operator.items():
        oldop = dict(operators=op.operator)
        oldgrid["Q2grid"][q2[0]] = oldop

    oldgrid["q2_ref"] = operator.mu20
    oldgrid["targetpids"] = operator.bases.targetpids
    oldgrid["targetgrid"] = operator.bases.targetgrid.raw
    # The EKO contains the rotation matrix but we pass the list of
    # evol basis pids to pineappl.
    oldgrid["inputpids"] = basis_rotation.evol_basis_pids
    oldgrid["inputgrid"] = operator.bases.inputgrid.raw

    return oldgrid

"""Compatibility layer for EKO migration."""
from typing import Any, Dict

from eko.output.struct import EKO


def pineappl_layout(operator: EKO) -> Dict[str, Any]:
    """Extract information required by :func:`pineappl.grid.Grid.convolute_eko`.

    Parameters
    ----------
    operator: EKO
        an evolution operator in the new layout

    Returns
    -------
    dict
        a minimal object, with all and only the information consumed by PineAPPL

    """
    oldgrid = {}
    oldgrid["Q2grid"] = {}
    for q2, op in operator.items():
        oldop = dict(operators=op.operator)
        oldgrid["Q2grid"][q2] = oldop

    oldgrid["q2_ref"] = operator.Q02
    oldgrid["targetpids"] = operator.rotations.targetpids
    oldgrid["targetgrid"] = operator.rotations.targetgrid.raw
    oldgrid["inputpids"] = operator.rotations.inputpids
    oldgrid["inputgrid"] = operator.rotations.inputgrid.raw

    return oldgrid

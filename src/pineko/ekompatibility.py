"""Compatibility layer for EKO migration."""
from typing import Any, Dict

import eko.output
import eko.output.legacy
from eko.output.struct import EKO

from . import check


def pineappl_layout(operator: EKO, targetgrid) -> Dict[str, Any]:
    """Extract information required by :func:`pineappl.grid.Grid.convolute_eko`.

    Parameters
    ----------
    operator: EKO
        an evolution operator in the new layout
    targetgrid: np.NDarray
        x_grid of the process scale

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
    oldgrid["targetgrid"] = targetgrid
    oldgrid["inputpids"] = operator.rotations.inputpids
    oldgrid["inputgrid"] = operator.rotations.inputgrid.raw

    return oldgrid


def load(eko_filename):
    """Check if the input eko_filename is a legacy or a new eko operator and load it accordingly."""
    if check.check_eko_is_legacy(eko_filename):
        operators = eko.output.legacy.load_tar(eko_filename)
    else:
        operators = eko.output.EKO.load(eko_filename)
    return operators

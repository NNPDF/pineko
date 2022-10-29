"""Tools related to theory cards."""
import pathlib
from typing import Any, Dict

import yaml

from . import configs


def path(theory_id: int) -> pathlib.Path:
    """Determine path to theory card.

    Parameters
    ----------
    theory_id : int
        theory id

    Returns
    -------
    pathlib.Path
        theory card path

    """
    return configs.configs["paths"]["theory_cards"] / f"{theory_id}.yaml"


def load(theory_id: int) -> Dict[str, Any]:
    """Load a theory card.

    Parameters
    ----------
    theory_id : int
        theory id

    Returns
    -------
    theory_card : dict
        theory card

    """
    with open(path(theory_id), encoding="utf-8") as f:
        theory_card = yaml.safe_load(f)
    return theory_card


def construct_assumptions(tcard):
    """Compute the assumptions hash from the theory settings.

    The used informations are the scale :math:`Q_0` of the FK table,
    the matching scales of the heavy quarks and whether an intrinsic component of the charm is
    allowed.

    Parameters
    ----------
    tcard : dict
        theory card

    Returns
    -------
    str
        assumptions hash
    """
    # retrieve the relevant info from theory card
    Q0 = tcard["Q0"]
    match_scales = {
        "c": tcard["kcThr"] * tcard["mc"],
        "b": tcard["kbThr"] * tcard["mb"],
        "t": tcard["ktThr"] * tcard["mt"],
    }
    ic = tcard["IC"]
    hash_ = "Nf"
    act_flav = 6
    mod = "Ind"
    if Q0 < match_scales["t"]:
        act_flav = 5
    if Q0 < match_scales["b"]:
        act_flav = 4
    if Q0 < match_scales["c"]:
        act_flav = 3
        if ic:
            act_flav += 1
            mod = "Sym"
    hash_ += str(act_flav) + mod
    return hash_

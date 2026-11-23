"""Tools related to theory cards."""

import pathlib
from typing import Any, Dict

import yaml

from . import configs
from .utils import load_nnpdf_theory


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
    return configs.configs["paths"][configs.THEORY_PATH_KEY] / f"{theory_id}.yaml"


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
    nnpdf_theory = load_nnpdf_theory(theory_id, configs.configs)
    if nnpdf_theory is not None:
        return nnpdf_theory

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
    hash_ += str(act_flav) + mod
    return hash_


def qed_running_alpha(tcard):
    """Return the boundary value at ``Qref`` of the running QED coupling, for EKO.

    This is ``alpha_qed_running_mz`` when the theory card gives it (it then requires
    ``Qref = MZ``), since ``alphaqed`` is then a fixed electroweak-scheme coupling such as
    alpha_Gmu that does not obey the QED renormalisation group equation. Otherwise it is
    ``alphaqed`` (as in NNPDF4.0QED, where alphaqed = 1/128.94 at 91.2 GeV). Must stay
    consistent with ``nnpdf_data.theory.qed_running_alpha`` (NNPDF/nnpdf#2541).

    Parameters
    ----------
    tcard : dict
        theory card

    Returns
    -------
    float
        alpha_em at ``Qref`` to be used as boundary condition of the QED running
    """
    alpha_qed_running_mz = tcard.get("alpha_qed_running_mz")
    if alpha_qed_running_mz is None:
        return tcard["alphaqed"]
    if abs(tcard["MZ"] - tcard["Qref"]) > 1e-6 * tcard["MZ"]:
        raise ValueError(
            "alpha_qed_running_mz requires Qref = MZ, "
            f"got Qref = {tcard['Qref']}, MZ = {tcard['MZ']}"
        )
    return alpha_qed_running_mz

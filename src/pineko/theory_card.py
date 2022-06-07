# -*- coding: utf-8 -*-
import yaml

from . import configs


def load(theory_id):
    """
    Load a theory card.

    Parameters
    ----------
    theory_id : int
        theory id

    Returns
    -------
    theory_card : dict
        theory card
    """
    tcard_path = configs.configs["paths"]["theory_cards"] / f"{theory_id}.yaml"
    with open(tcard_path, encoding="utf-8") as f:
        theory_card = yaml.safe_load(f)
    return theory_card

def construct_assumption(tcard):
    """
    This function return the appropriate assumption hash according to the scale Q0 of the fktable,
    the matching scales of the heavy quarks and whether an intrinsic component of the charm is
    allowed.

    Parameters
    ----------
        tcard : dict
            theory card

    Returns
    -------
            : str
        assumption hash
    """
    # retrive the relevant info from theory card
    Q0 = tcard['Q0']
    match_scales = {'c' : tcard['kcThr']*tcard['mc'], 'b' : tcard['kbThr']*tcard['mb'] , 't' : tcard['ktThr']*tcard['mt'] }
    ic = tcard["IC"]
    hash = 'Nf'
    act_flav = 6
    mod = 'Ind'
    if Q0 < match_scales['t']:
        act_flav = 5
        if Q0 < match_scales['b']:
            act_flav = 4
            if Q0 < match_scales['c']:
                act_flav = 3
    hash += str(act_flav) + mod
    return hash

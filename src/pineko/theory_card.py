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

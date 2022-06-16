# -*- coding: utf-8 -*-
import click
import pineappl
import rich

from .. import check, theory_card
from ._base import command


@command.command("check_scalevar")
@click.argument("pineappl_path", metavar="PINEAPPL", type=click.Path(exists=True))
@click.argument("theory_ID", metavar="ID", type=click.Path(exists=True))
def subcommand(pineappl_path, theory_ID):
    """Check if PineAPPL grid contains scale variations if theory card needs them"""
    t_card = theory_card.load(theory_ID)
    xir = t_card["XIR"]
    xif = t_card["XIF"]
    ftr = t_card["fact_to_ren_scale_ratio"]
    check.check_grid_contains_sv(pineappl_path, xir, xif, ftr)

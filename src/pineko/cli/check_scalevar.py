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
    pineappl_grid = pineappl.grid.Grid.read(pineappl_path)
    check.check_grid_contains_sv(pineappl_grid, t_card)

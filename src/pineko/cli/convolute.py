# -*- coding: utf-8 -*-
import click

from .. import evolve
from ._base import command


@command.command("convolute")
@click.argument("pineappl", type=click.Path(exists=True))
@click.argument("eko", type=click.Path(exists=True))
@click.argument("fktable", type=click.Path())
@click.argument("max_as", type=int)
@click.argument("max_al", type=int)
@click.option(
    "--pdf", default=None, help="if given, print comparison table", show_default=True
)
def subcommand(pineappl, eko, fktable, max_as, max_al, pdf):
    """Convolute PineAPPL grid and EKO.

    PINEAPPL and EKO are the path to the respective elements to convolute, and
    FKTABLE is the path where to dump the output.
    Moreover, MAX_AS and MAX_AL are used to specify the order in QCD and QED
    couplings (i.e. the maximum power allowed for each correction).
    """
    _grid, _fk, comp = evolve.evolve_grid(pineappl, eko, fktable, max_as, max_al, pdf)
    if comp:
        print(comp.to_string())

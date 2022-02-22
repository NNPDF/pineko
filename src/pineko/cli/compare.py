# -*- coding: utf-8 -*-
import click

from .. import comparator
from ._base import command


@command.command("compare")
@click.argument("pineappl", type=click.Path(exists=True))
@click.argument("eko", type=click.Path(exists=True))
@click.argument("fktable", type=click.Path())
@click.argument("max_as", type=int)
@click.argument("max_al", type=int)
def subcommand(pineappl, fktable, max_as, max_al, pdf):
    """Compare process level PineAPPL grid and derived FkTable.

    The comparison between the grid stored at PINEAPPL path, and the table
    stored in FKTABLE, is performed by convoluting both the grids with the PDF
    set, evaluating its interpolation grid at the two different scales (thus
    comparing the EKO evolution, with the one stored inside LHAPDF grid).

    The comparison involves the orders in QCD and QED up to the maximum power
    of the coupling corresponding respectively to MAX_AS and MAX_AL.
    """
    comparator.compare(pineappl, fktable, max_as, max_al, pdf)

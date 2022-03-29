# -*- coding: utf-8 -*-
import click
import pineappl
import rich

from .. import comparator
from ._base import command


@command.command("compare")
@click.argument("pineappl_path", type=click.Path(exists=True))
@click.argument("fktable_path", type=click.Path())
@click.argument("max_as", type=int)
@click.argument("max_al", type=int)
@click.argument("pdf", type=str)
def subcommand(pineappl_path, fktable_path, max_as, max_al, pdf):
    """Compare process level PineAPPL grid and derived FkTable.

    The comparison between the grid stored at PINEAPPL_PATH, and the FK table
    stored at FKTABLE_PATH, is performed by convoluting both the grids with the PDF
    set, evaluating its interpolation grid at the two different scales (thus
    comparing the EKO evolution, with the one stored inside LHAPDF grid).

    The comparison involves the orders in QCD and QED up to the maximum power
    of the coupling corresponding respectively to MAX_AS and MAX_AL.
    """
    pine = pineappl.grid.Grid.read(pineappl_path)
    fk = pineappl.fk_table.FkTable.read(fktable_path)
    rich.print(comparator.compare(pine, fk, max_as, max_al, pdf))

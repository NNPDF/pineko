"""CLI entry point to comparison grid vs. FK Table."""
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
@click.option("--xir", default=1.0, help="renormalization scale variation")
@click.option("--xif", default=1.0, help="factorization scale variation")
def subcommand(pineappl_path, fktable_path, max_as, max_al, pdf, xir, xif):
    """Compare process level PineAPPL grid and derived FK Table.

    The comparison between the grid stored at PINEAPPL_PATH, and the FK table
    stored at FKTABLE_PATH, is performed by convoluting both the grids with the PDF
    set, evaluating its interpolation grid at the two different scales (thus
    comparing the EKO evolution, with the one stored inside LHAPDF grid).

    The comparison involves the orders in QCD and QED up to the maximum power
    of the coupling corresponding respectively to MAX_AS and MAX_AL.

    XIR and XIF represent the renormalization and factorization scale in the grid respectively.
    """
    pine = pineappl.grid.Grid.read(pineappl_path)
    fk = pineappl.fk_table.FkTable.read(fktable_path)
    # Note that we need to cast to string before printing to avoid ellipsis ...
    rich.print(comparator.compare(pine, fk, max_as, max_al, pdf, xir, xif).to_string())

"""CLI entry point to comparison grid vs. FK Table."""

import pineappl
import rich
import rich_click as click

from .. import comparator
from ._base import command


@command.command("compare")
@click.argument("fktable_path", type=click.Path())
@click.argument("grid_path", type=click.Path(exists=True))
@click.argument("max_as", type=int)
@click.argument("max_al", type=int)
@click.argument("pdfs", type=click.STRING, nargs=-1)
@click.option("--xir", default=1.0, help="renormalization scale variation")
@click.option("--xif", default=1.0, help="factorization scale variation")
@click.option("--xia", default=1.0, help="fragmentation scale variation")
@click.option(
    "--as_pdf_idx",
    type=int,
    default=0,
    help="Index (starting from 0) of the PDF to be used to compute `alpha_s(Q^2)`",
)
@click.option(
    "--threshold", default=5.0, help="threshold in permille to accept Grid -> FK"
)
@click.option(
    "--q2_min", default=1.0, help="minimum value of Q2 to check the predictions"
)
def subcommand(
    fktable_path,
    grid_path,
    max_as,
    max_al,
    pdfs,
    xir,
    xif,
    xia,
    as_pdf_idx,
    threshold,
    q2_min,
):
    """Compare process level PineAPPL grid and derived FK Table.

    The comparison between the grid stored at PINEAPPL_PATH, and the FK table
    stored at FKTABLE_PATH, is performed by convoluting both the grids with the PDF
    set, evaluating its interpolation grid at the two different scales (thus
    comparing the EKO evolution, with the one stored inside LHAPDF grid).

    The comparison involves the orders in QCD and QED up to the maximum power
    of the coupling corresponding respectively to MAX_AS and MAX_AL.

    XIR, XIF, and XIA represent the renormalization, factorization, and fragmentation
    scale in the grid, respectively.
    """
    pine = pineappl.grid.Grid.read(grid_path)
    fk = pineappl.fk_table.FkTable.read(fktable_path)

    if len(pine.convolutions) != len(pdfs) and len(pdfs) != 1:
        raise ValueError("The number of PDFs is inconsistent with the Grid!")

    # Define the variations of scales as tuple
    scales = (xir, xif, xia)

    # Note that we need to cast to string before printing to avoid ellipsis ...
    comparisons = comparator.compare(
        pine, fk, max_as, max_al, pdfs, scales, as_pdf_idx, threshold, q2_min
    )
    rich.print(comparisons.to_string())

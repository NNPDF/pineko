"""CLI entry point to the operator card generation."""
import click
import rich

from .. import evolve
from ._base import command


@command.command("opcard")
@click.argument("pineappl-path", metavar="PINEAPPL", type=click.Path(exists=True))
@click.argument(
    "default-card-path", metavar="DEFAULT_CARD", type=click.Path(exists=True)
)
@click.argument("thcard-path", metavar="THCARD", type=click.Path())
@click.argument("opcard-path", metavar="OPCARD", type=click.Path())
@click.option("--xif", default=1.0, help="factorization scale variation")
def subcommand(pineappl_path, default_card_path, thcard_path, opcard_path, xif):
    """Write EKO card for PineAPPL grid.

    Writes a copy of the default card from DEFAULT_CARD to OPCARD
    with the adjusted x grid and Q2 grid read from PINEAPPL.

    A THCARD is required, since some of the EKO's OPCARD information come from
    the NNPDF theory entries (e.g. :math:`Q0`).

    XIF is the factorization scale variation.

    """
    _x_grid, q2_grid = evolve.write_operator_card_from_file(
        pineappl_path, default_card_path, opcard_path, xif, thcard_path
    )
    rich.print(
        f"[green]Success:[/] Wrote card with {len(q2_grid)} Q2 points to {opcard_path}"
    )

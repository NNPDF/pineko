# -*- coding: utf-8 -*-
import click
import rich

from .. import evolve
from ._base import command


@command.command("opcard")
@click.argument("pineappl_path", metavar="PINEAPPL", type=click.Path(exists=True))
@click.argument(
    "default_card_path", metavar="DEFAULT_CARD", type=click.Path(exists=True)
)
@click.argument("opcard_path", metavar="OPCARD", type=click.Path())
def subcommand(pineappl_path, default_card_path, opcard_path):
    """Write EKO card for PineAPPL grid.

    Writes a copy of the default card from DEFAULT_CARD to OPCARD
    with the adjusted x grid and Q2 grid read from PINEAPPL.
    """
    _x_grid, q2_grid = evolve.write_operator_card_from_file(
        pineappl_path, default_card_path, opcard_path
    )
    rich.print(
        f"[green]Success:[/] Wrote card with {len(q2_grid)} Q2 points to {opcard_path}"
    )

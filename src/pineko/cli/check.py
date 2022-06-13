# -*- coding: utf-8 -*-
"""CLI entry point to check compatibility."""
import click
import eko.output
import pineappl
import rich

from .. import check
from ._base import command


@command.command("check")
@click.argument("pineappl_path", metavar="PINEAPPL", type=click.Path(exists=True))
@click.argument("eko_path", metavar="EKO", type=click.Path(exists=True))
@click.option("--xif", default=1.0, help="factorization scale variation")
def subcommand(pineappl_path, eko_path, xif):
    """Check PineAPPL grid and EKO compatibility.

    In order to be compatible, the grid provided in PINEAPPL and the operator
    provided in EKO, have to expose the same x grid and Q2 grid.

    XIF is the factorization scale variation.
    """
    pineappl_grid = pineappl.grid.Grid.read(pineappl_path)
    operators = eko.output.Output.load_tar(eko_path)
    try:
        check.check_grid_and_eko_compatible(pineappl_grid, operators, xif)
        rich.print("[green]Success:[/] grids are compatible")
    except ValueError as e:
        rich.print("[red]Error:[/]", e)


@command.command("check_scalevar")
@click.argument("pineappl_path", metavar="PINEAPPL", type=click.Path(exists=True))
@click.argument("theory_ID", metavar="ID", type=click.Path(exists=True))
def subcommand(pineappl_path, theory_ID):
    """Check if PineAPPL grid contains scale variations if theory card needs them."""
    theory_card = theory_card.load(theory_ID)
    pineappl_grid = pineappl.grid.Grid.read(pineappl_path)
    check.check_grid_contains_sv(pineappl_grid, theory_card)

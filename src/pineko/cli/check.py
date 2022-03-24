# -*- coding: utf-8 -*-
import click
import eko.output
import pineappl
import rich

from .. import check
from ._base import command


@command.command("check")
@click.argument("pineappl_path", metavar="PINEAPPL", type=click.Path(exists=True))
@click.argument("eko_path", metavar="EKO", type=click.Path(exists=True))
def subcommand(pineappl_path, eko_path):
    """Check PineAPPL grid and EKO compatibility.

    In order to be compatible, the grid provided in PINEAPPL and the operator
    provided in EKO, have to expose the same x grid and Q2 grid.
    """
    pineappl_grid = pineappl.grid.Grid.read(pineappl_path)
    operators = eko.output.Output.load_tar(eko_path)
    try:
        check.check_grid_and_eko_compatible(pineappl_grid, operators)
        rich.print("[green]Success:[/] grids are compatible")
    except ValueError as e:
        rich.print("[red]Error:[/]", e)

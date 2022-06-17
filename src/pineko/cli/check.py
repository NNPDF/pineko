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
@click.option(
    "--tocheck",
    required=True,
    type=str,
    default=None,
    help="scale variations to check (xir or xif)",
    show_default=True,
)
def subcommand_sv(pineappl_path, tocheck):
    """Check if PineAPPL grid contains requested scale variations"""
    if tocheck == "xir":
        try:
            check.check_grid_contains_ren_sv(pineappl_path)
            rich.print(
                "[green]Success:[/] grids contain renormalization scale variations"
            )
        except ValueError as e:
            rich.print("[red]Error:[/]", e)
    elif tocheck == "xif":
        try:
            check.check_grid_contains_fact_sv(pineappl_path)
            rich.print(
                "[green]Success:[/] grids contain factorization scale variations"
            )
        except ValueError as e:
            rich.print("[red]Error:[/]", e)
    else:
        raise ValueError("Scale variation to check can be one between xir and xif")

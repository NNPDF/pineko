"""CLI entry point to check compatibility."""
from collections import namedtuple
from enum import Enum, auto

import click
import eko.output.legacy
import pineappl
import rich

from .. import check
from ._base import command


@command.group("check")
def subcommand():
    """Check grid and operator properties."""


@subcommand.command("compatibility")
@click.argument("grid_path", metavar="PINEAPPL", type=click.Path(exists=True))
@click.argument("operator_path", metavar="EKO", type=click.Path(exists=True))
@click.option("--xif", default=1.0, help="factorization scale variation")
def sub_compatibility(grid_path, operator_path, xif):
    """Check PineAPPL grid and EKO compatibility.

    In order to be compatible, the grid provided in PINEAPPL and the operator
    provided in EKO, have to expose the same x grid and Q2 grid.

    XIF is the factorization scale variation.

    """
    pineappl_grid = pineappl.grid.Grid.read(grid_path)
    operators = eko.output.legacy.load_tar(operator_path)
    try:
        check.check_grid_and_eko_compatible(pineappl_grid, operators, xif)
        rich.print("[green]Success:[/] grids are compatible")
    except ValueError as e:
        rich.print("[red]Error:[/]", e)


CouplingInfo = namedtuple("CouplingInfo", ["descr", "theory"])


class Coupling(Enum):
    """Auxiliary class to list the possible couplings."""

    AS = CouplingInfo("strong", "QCD")
    AL = CouplingInfo("electromagnetic", "QED")


ScaleValue = namedtuple("ScaleValue", ["descr", "check"])


class Scale(Enum):
    """Auxiliary class to list the possible scale variations."""

    REN = ScaleValue("renormalization scale variations", check.contains_ren)
    FACT = ScaleValue("factorization scale variations", check.contains_fact)


@subcommand.command("scvar")
@click.argument("grid_path", metavar="PINEAPPL", type=click.Path(exists=True))
@click.argument(
    "scale",
    metavar="SCALE",
    type=click.Choice(list(el.name for el in Scale), case_sensitive=False),
)
@click.argument("max_as_order", metavar="AS_ORDER", type=int)
@click.argument("max_al_order", metavar="AL_ORDER", type=int)
def sub_scvar(grid_path, scale, max_as_order, max_al_order):
    """Check if PineAPPL grid contains requested scale variations for the requested order."""
    grid = pineappl.grid.Grid.read(grid_path)
    grid.optimize()
    success = "[green]Success:[/] grids contain"
    error = "[red]Error:[/] grids do not contain"
    # Call the function
    try:
        conditions = Scale[scale].value.check(grid, max_as_order, max_al_order)
    except KeyError:
        raise ValueError("Scale variation to check can be one between ren and fact")
    for coupling, condition in zip(Coupling, conditions):
        to_write = ""
        if condition:
            to_write += success
        else:
            to_write += error
        to_write += " " + Scale[scale].value.descr
        to_write += f" for {coupling.name.lower()}"
        rich.print(to_write)

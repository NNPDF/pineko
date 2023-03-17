"""CLI entry point to check compatibility."""
from collections import namedtuple
from enum import Enum

import click
import eko
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
    with eko.EKO.read(operator_path) as operators:
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


@subcommand.command("scvar")
@click.argument("grid_path", metavar="PINEAPPL", type=click.Path(exists=True))
@click.argument(
    "scale",
    metavar="SCALE",
    type=click.Choice(list(el.name for el in check.Scale), case_sensitive=False),
)
@click.argument("max_as_order", metavar="AS_ORDER", type=int)
@click.argument("max_al_order", metavar="AL_ORDER", type=int)
def sub_scvar(grid_path, scale, max_as_order, max_al_order):
    """Check if PineAPPL grid contains requested scale variations for the requested order."""
    grid = pineappl.grid.Grid.read(grid_path)
    grid.optimize()
    success = "[green]Success:[/] grids contain"
    warning = "[orange]Warning:[/] grids do not contain central order for requested"
    error = "[red]Error:[/] grids do not contain"
    # Call the function
    scaleobj = check.Scale[scale]
    checkres, max_as_effective = check.contains_sv(
        grid, max_as_order, max_al_order, scaleobj
    )
    sv_as = None
    central_as = None
    # TODO: fix this
    if max_as_effective == max_as_order:
        if checkres is check.CheckMax.BOTH:
            sv_as = True
            central_as = True
        elif checkres is check.CheckMax.CENTRAL:
            sv_as = False
            central_as = True
        else:
            sv_as = False
            central_as = False
    sv_conditions = [sv_as, True]
    cen_conditions = [central_as, True]
    for coupling, sv_condition, cen_condition in zip(
        Coupling, sv_conditions, cen_conditions
    ):
        to_write = ""
        if sv_condition and cen_condition:
            to_write += success
        elif sv_condition and not cen_condition:
            to_write += warning
        else:
            to_write += error
        to_write += " " + check.Scale[scale].value.descr
        to_write += f" for {coupling.name.lower()}"
        rich.print(to_write)

"""CLI entry point to the operator card generation."""

import pathlib

import rich
import rich_click as click
import yaml

from .. import evolve
from ._base import command


@command.command("opcard")
@click.argument("pineappl-path", metavar="PINEAPPL", type=click.Path(exists=True))
@click.argument("thcard-path", metavar="THCARD", type=click.Path())
@click.argument("opcard-path", metavar="OPCARD", type=click.Path())
@click.option(
    "--ipd", default=4, show_default=True, help="interpolation polynomial degree"
)
@click.option("--iil", default=True, show_default=True, help="interpolation is log")
@click.option(
    "--int-cores", default=1, show_default=True, help="number of integration cores"
)
def subcommand(
    pineappl_path,
    thcard_path,
    opcard_path,
    ipd,
    iil,
    int_cores,
):
    """Write EKO card for PineAPPL grid.

    Writes an operator card OPCARD from the information in
    opcard_template.py and the theory card.

    A THCARD is required, since some of the EKO's OPCARD information come from
    the NNPDF theory entries (e.g. :math:`Q0`).

    """
    tcard = yaml.safe_load(pathlib.Path(thcard_path).read_text(encoding="utf-8"))
    opcard_path = pathlib.Path(opcard_path)
    _x_grid, q2_grid = evolve.write_operator_card_from_file(
        pineappl_path, opcard_path, tcard, ipd, iil, int_cores
    )

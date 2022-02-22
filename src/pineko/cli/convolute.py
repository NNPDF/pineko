# -*- coding: utf-8 -*-
import click

from .. import evolve
from ._base import command


@command.command("convolute")
@click.argument("pineappl", type=click.Path(exists=True))
@click.argument("eko", type=click.Path(exists=True))
@click.argument("fktable", type=click.Path())
@click.argument("max_as", type=int)
@click.argument("max_al", type=int)
@click.option(
    "--pdf", default=None, help="if given, print comparison table", show_default=True
)
def subcommand(pineappl, eko, fktable, max_as, max_al, pdf):
    """Convolute PineAPPL grid and EKO, to obtain the resulting fktable.

    `pineappl` and `eko` are the path to the respective elements to convolute,
    and `fktable` is the path where to dump the output.
    Moreover, `max_as` and `max_al` are used to specify the order in QCD and
    QED couplings (i.e. the maximum power allowed for each correction).
    """
    evolve.evolve_grid(pineappl, eko, fktable, max_as, max_al, pdf)

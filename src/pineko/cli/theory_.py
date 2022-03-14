# -*- coding: utf-8 -*-
import click

from .. import theory
from ._base import command


@command.group("theory")
def theory_():
    """Iterate a subcommand on a given theory and list of datasets"""


@theory_.command()
@click.argument("theory_id", type=click.INT)
@click.argument("datasets", type=click.STRING, nargs=-1)
def opcards(theory_id, datasets):
    """Write EKO card for all FK tables in all datasets."""
    theory.TheoryBuilder(theory_id, datasets).opcards()


@theory_.command()
@click.argument("theory_id", type=click.INT)
@click.argument("datasets", type=click.STRING, nargs=-1)
@click.option("--logs", is_flag=True, help="dump logs")
def ekos(theory_id, datasets, logs):
    """Compute EKOs for all FK tables in all datasets."""
    theory.TheoryBuilder(theory_id, datasets).ekos(logs)


@theory_.command()
@click.argument("theory_id", type=click.INT)
@click.argument("datasets", type=click.STRING, nargs=-1)
@click.option("--pdf", "-p", default=None, help="comparison PDF")
@click.option("--logs", is_flag=True, help="dump comparison")
def fks(theory_id, datasets, pdf, logs):
    """Compute FK tables in all datasets."""
    theory.TheoryBuilder(theory_id, datasets).fks(pdf, logs)

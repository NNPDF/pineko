# -*- coding: utf-8 -*-
import click

from .. import theory
from ._base import command


@command.command("theory_ekos")
@click.argument("theory_id", type=click.INT)
@click.argument("datasets", type=click.STRING, nargs=-1)
@click.option("--logs", is_flag=True, help="dump logs")
def subcommand(theory_id, datasets, logs):
    """Compute EKOs for all FK tables in all datasets."""
    theory.TheoryBuilder(theory_id, datasets).ekos(logs)

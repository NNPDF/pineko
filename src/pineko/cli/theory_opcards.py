# -*- coding: utf-8 -*-
import click

from .. import theory
from ._base import command


@command.command("theory_opcards")
@click.argument("theory_id", type=click.INT)
@click.argument("datasets", type=click.STRING, nargs=-1)
def subcommand(theory_id, datasets):
    """Write EKO card for all FK tables in all datasets."""
    theory.TheoryBuilder(theory_id, datasets).opcards()

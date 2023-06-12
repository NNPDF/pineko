"""CLI entry point to FONLL."""
import click

from .. import fonll
from ._base import command


class InconsistentInputsError(Exception):
    """Raised if the inputs are not consistent with FONLL accounting for
    only charm mass, or both charm and bottom masses"""

    pass


@command.command("fonll")
@click.argument("FFNS3", type=click.Path(exists=True))
@click.argument("FFN03", type=click.Path(exists=True))
@click.argument("FFNS4", type=click.Path(exists=True))
@click.argument("theoryID", type=int)
@click.option("--FFN04", type=click.Path(exists=True))
@click.option("--FFNS5", type=click.Path(exists=True))
def subcommand(ffns3, ffn03, ffns4, ffn04, ffns5, theoryid):
    """ """
    if ffn04 == None and ffns5 != None or ffn04 != None and ffns5 == None:
        raise InconsistentInputsError(
            """To account for bottom mass effects in FONLL fktables in both
            FFN04 and FFNS5 schemes are required. Currently only one is provided."""
        )
    fonll.produce_combined_fk(ffns3, ffn03, ffns4, ffn04, ffns5, theoryid)

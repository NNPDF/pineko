"""CLI entry point to FONLL."""
import click

from .. import configs, fonll, theory_card
from ._base import command


class TheoryCardError(Exception):
    """Raised when asked for FONLL theory cards with an original tcard as input
    that is not asking for FONLL"""

    pass


class InconsistentInputsError(Exception):
    """Raised if the inputs are not consistent with FONLL accounting for
    only charm mass, or both charm and bottom masses"""

    pass


@command.command("combine_fonll")
@click.argument("FFNS3", type=click.Path(exists=True))
@click.argument("FFN03", type=click.Path(exists=True))
@click.argument("FFNS4", type=click.Path(exists=True))
@click.argument("theoryID", type=int)
@click.option("--FFN04", type=click.Path(exists=True))
@click.option("--FFNS5", type=click.Path(exists=True))
def subcommand(ffns3, ffn03, ffns4, ffn04, ffns5, theoryid):
    """Combines the different FKs needed to produce the FONLL prescription."""
    if ffn04 == None and ffns5 != None or ffn04 != None and ffns5 == None:
        raise InconsistentInputsError(
            """To account for bottom mass effects in FONLL fktables in both
            FFN04 and FFNS5 schemes are required. Currently only one is provided."""
        )
    fonll.produce_combined_fk(ffns3, ffn03, ffns4, ffn04, ffns5, theoryid)


@command.command("fonll_tcards")
@click.argument("theoryID", type=int)
def fonll_tcards(theoryid):
    """Produce the FONLL tcards starting from the original tcard given by the theoryID"""
    configs.configs = configs.defaults(configs.load())
    tcard = theory_card.load(theoryid)
    tcard_parent_path = theory_card.path(theoryid).parent
    if "FONLL" not in tcard["FNS"]:
        raise TheoryCardError
    fonll.produce_fonll_tcards(tcard, tcard_parent_path)

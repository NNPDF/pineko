"""CLI entry point to FONLL."""
import click

from .. import configs, fonll, theory_card
from ._base import command


class TheoryCardError(Exception):
    """Raised when asked for FONLL theory cards with an original tcard as input that is not asking for FONLL."""

    pass


class InconsistentInputsError(Exception):
    """Raised if the inputs are not consistent with FONLL."""

    pass


@command.command("combine_fonll")
@click.argument("FFNS3", type=click.Path(exists=True))
@click.argument("FFN03", type=click.Path(exists=True))
@click.argument("FFNS4til", type=click.Path(exists=True))
@click.argument("theoryID", type=int)
@click.option("--FFNS4bar", type=click.Path(exists=True))
@click.option("--FFN04", type=click.Path(exists=True))
@click.option("--FFNS5til", type=click.Path(exists=True))
@click.option("--FFNS5bar", type=click.Path(exists=True))
def subcommand(ffns3, ffn03, ffns4til, theoryid, ffns4bar, ffn04, ffns5til, ffns5bar):
    """Combine the different FKs needed to produce the FONLL prescription."""
    if (ffn04 is None and ffns5til is not None) or (
        ffn04 is not None and ffns5til is None
    ):
        print(
            "One between ffn04 and ffns5til has been provided without the other. Since they are both needed to construct FONLL, this does not make sense."
        )
        raise InconsistentInputsError
    configs.configs = configs.defaults(configs.load())
    tcard = theory_card.load(theoryid)
    if not "DAMPPOWER" in tcard:
        if tcard["DAMP"] != 0:
            raise InconsistentInputsError
        tcard["DAMPPOWER"] = None
    fonll.produce_combined_fk(
        ffns3,
        ffn03,
        ffns4til,
        ffns4bar,
        ffn04,
        ffns5til,
        ffns5bar,
        theoryid,
        damp=(tcard["DAMP"], tcard["DAMPPOWER"]),
    )


@command.command("fonll_tcards")
@click.argument("theoryID", type=int)
def fonll_tcards(theoryid):
    """Produce the FONLL tcards starting from the original tcard given by the theoryID."""
    configs.configs = configs.defaults(configs.load())
    tcard = theory_card.load(theoryid)
    tcard_parent_path = theory_card.path(theoryid).parent
    if "FONLL" not in tcard["FNS"]:
        raise TheoryCardError
    _ = fonll.produce_fonll_tcards(tcard, tcard_parent_path, theoryid)

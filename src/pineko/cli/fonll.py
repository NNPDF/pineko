"""CLI entry point to FONLL."""
import click
import rich

from .. import configs, fonll, parser, theory_card
from ._base import command


class TheoryCardError(Exception):
    """Raised when asked for FONLL theory cards with an original tcard as input that is not asking for FONLL."""

    pass


class InconsistentInputsError(Exception):
    """Raised if the inputs are not consistent with FONLL."""

    pass


def get_list_grids_name(yaml_file):
    """Return the list of the grids in the yaml file."""
    yaml_content = parser._load_yaml(yaml_file)
    # Turn the operands and the members into paths (and check all of them exist)
    ret = []
    for operand in yaml_content["operands"]:
        for member in operand:
            ret.append(f"{member}.{parser.EXT}")
    return ret


@command.command("combine_fonll")
@click.argument("theoryID", type=int)
@click.argument("dataset", type=str)
@click.option("--FFNS3", type=int, help="theoryID containing the ffns3 fktable")
@click.option("--FFN03", type=int, help="theoryID containing the ffn03 fktable")
@click.option("--FFNS4til", type=int, help="theoryID containing the ffns4til fktable")
@click.option("--FFNS4bar", type=int, help="theoryID containing the ffns4bar fktable")
@click.option("--FFN04", type=int, help="theoryID containing the ffn04 fktable")
@click.option("--FFNS5til", type=int, help="theoryID containing the ffns5til fktable")
@click.option("--FFNS5bar", type=int, help="theoryID containing the ffns5bar fktable")
@click.option("--overwrite", is_flag=True, help="Allow files to be overwritten")
def subcommand(
    theoryid,
    dataset,
    ffns3,
    ffn03,
    ffns4til,
    ffns4bar,
    ffn04,
    ffns5til,
    ffns5bar,
    overwrite,
):
    """Combine the different FKs needed to produce the FONLL prescription."""
    # Checks
    if (ffn04 is None and ffns5til is not None) or (
        ffn04 is not None and ffns5til is None
    ):
        print(
            "One between ffn04 and ffns5til has been provided without the other. Since they are both needed to construct FONLL, this does not make sense."
        )
        raise InconsistentInputsError
    if (ffn03 is None and ffns4til is not None) or (
        ffn03 is not None and ffns4til is None
    ):
        print(
            "One between ffn03 and ffns4til has been provided without the other. Since they are both needed to construct FONLL, this does not make sense."
        )
        raise InconsistentInputsError
    # Get theory info
    configs.configs = configs.defaults(configs.load())
    tcard = theory_card.load(theoryid)
    if not "DAMPPOWER" in tcard:
        if tcard["DAMP"] != 0:
            raise InconsistentInputsError
        tcard["DAMPPOWER"] = None
    # Getting the paths to the grids
    grids_name = get_list_grids_name(
        configs.configs["paths"]["ymldb"] / f"{dataset}.yaml"
    )
    for grid in grids_name:
        # Checking if it already exists
        if (configs.configs["paths"]["fktables"] / str(theoryid) / grid).exists():
            if not overwrite:
                rich.print(f"Skipping existing FK Table {grid}")
                return
        fonll.produce_combined_fk(
            configs.configs["paths"]["fktables"] / str(ffns3) / grid
            if (configs.configs["paths"]["fktables"] / str(ffns3) / grid).exists()
            else None,
            configs.configs["paths"]["fktables"] / str(ffn03) / grid
            if (configs.configs["paths"]["fktables"] / str(ffn03) / grid).exists()
            else None,
            configs.configs["paths"]["fktables"] / str(ffns4til) / grid
            if (configs.configs["paths"]["fktables"] / str(ffns4til) / grid).exists()
            else None,
            configs.configs["paths"]["fktables"] / str(ffns4bar) / grid
            if (configs.configs["paths"]["fktables"] / str(ffns4bar) / grid).exists()
            else None,
            configs.configs["paths"]["fktables"] / str(ffn04) / grid
            if (configs.configs["paths"]["fktables"] / str(ffn04)).exists()
            else None,
            configs.configs["paths"]["fktables"] / str(ffns5til) / grid
            if (configs.configs["paths"]["fktables"] / str(ffns5til) / grid).exists()
            else None,
            configs.configs["paths"]["fktables"] / str(ffns5bar) / grid
            if (configs.configs["paths"]["fktables"] / str(ffns5bar) / grid).exists()
            else None,
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

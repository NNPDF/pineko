"""CLI entry point to FONLL."""

import pathlib

import click
import rich

from .. import configs, fonll, theory, theory_card
from ..fonll import TheoryCardError
from ._base import command



config_setting = click.option(
    "-c",
    "--configs",
    "cfg",
    default=None,
    type=click.Path(resolve_path=True, path_type=pathlib.Path),
    help="Explicitly specify config file (it has to be a valid TOML file).",
)


def load_config(cfg):
    """Iterate a subcommand on a given theory and list of datasets."""
    path = configs.detect(cfg)
    base_configs = configs.load(path)
    configs.configs = configs.defaults(base_configs)
    if cfg is not None:
        print(f"Configurations loaded from '{path}'")


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
@config_setting
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
    cfg,
):
    """Combine the different FKs needed to produce the FONLL prescription."""
    load_config(cfg)
    fonll.assembly_combined_fk(
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
        cfg,
    )


@command.command("fonll_tcards")
@click.argument("theoryID", type=int)
@config_setting
def fonll_tcards(theoryid, cfg):
    """Produce the FONLL tcards starting from the original tcard given by the theoryID."""
    load_config(cfg)

    tcard = theory_card.load(theoryid)
    tcard_parent_path = theory_card.path(theoryid).parent
    if "FONLL" not in tcard["FNS"]:
        raise TheoryCardError("The theorycard does not correspond to an FONLL scheme.")
    fonll.dump_tcards(tcard, tcard_parent_path, theoryid)

@command.command("fonll_ekos")
@click.argument("theoryID", type=click.INT)
@click.argument("datasets", type=click.STRING, nargs=-1)
@click.option("--overwrite", is_flag=True, help="Allow files to be overwritten")
@config_setting
def fonll_ekos(theoryid, datasets, overwrite, cfg):
    """Command to generate numerical FONLL ekos.

    1. Produce the 7 theory cards needed for numerical FONLL.
    2. Create the 3 operator cards for the different flavor patches.
    3. Run the 3 ekos for the different flavor patches.
    4. Inherit the ekos.
    """
    load_config(cfg)

    # create the 7 theory cards
    tcard = theory_card.load(theoryid)
    tcard_parent_path = theory_card.path(theoryid).parent
    if "FONLL" not in tcard["FNS"]:
        raise TheoryCardError("The theorycard does not correspond to an FONLL scheme.")
    fonll.dump_tcards(tcard, tcard_parent_path, theoryid)

    for nf_id in ["00", "04", "05"]:
        # create opcards
        theory.TheoryBuilder(
            f"{theoryid}{nf_id}", datasets, overwrite=overwrite
        ).opcards()

        # run the ekos
        theory.TheoryBuilder(
            f"{theoryid}{nf_id}",
            datasets,
            silent=False,
            clear_logs=True,
            overwrite=overwrite,
        ).ekos()

    # now inherit ekos
    # nf=3
    rich.print(f"[green] Inherit nf=3 ekos from theory {theoryid}00")
    theory.TheoryBuilder(f"{theoryid}00", datasets, overwrite=overwrite).inherit_ekos(
        f"{theoryid}01"
    )
    # nf=4
    rich.print(f"[green] Inherit nf=4 ekos from theory {theoryid}04")
    theory.TheoryBuilder(f"{theoryid}04", datasets, overwrite=overwrite).inherit_ekos(
        f"{theoryid}02"
    )
    theory.TheoryBuilder(f"{theoryid}04", datasets, overwrite=overwrite).inherit_ekos(
        f"{theoryid}03"
    )
    # nf=5
    rich.print(f"[green] Inherit nf=5 ekos from theory {theoryid}05")
    theory.TheoryBuilder(f"{theoryid}05", datasets, overwrite=overwrite).inherit_ekos(
        f"{theoryid}06"
    )


@command.command("fonll_fks")
@click.argument("theoryID", type=click.INT)
@click.argument("datasets", type=click.STRING, nargs=-1)
@click.option("--pdf", "-p", default=None, help="PDF set used for comparison")
@click.option("--overwrite", is_flag=True, help="Allow files to be overwritten")
@config_setting
def fonll_fks(theoryid, datasets, pdf, overwrite, cfg):
    """Command to generate numerical FONLL FK tables.

    1. Produce the 7 FK tables needed for numerical FONLL.
    2. Combine the FKtables into a single one.
    """
    load_config(cfg)

    # create the 7 FK tables
    for th_suffix in range(0, 7):
        theory.TheoryBuilder(
            f"{theoryid}0{th_suffix}",
            datasets,
            silent=False,
            clear_logs=True,
            overwrite=overwrite,
        ).fks(pdf)

    # combine
    for dataset in datasets:
        fonll.assembly_combined_fk(
            theoryid,
            dataset,
            ffns3=f"{theoryid}00",
            ffn03=f"{theoryid}01",
            ffns4til=f"{theoryid}02",
            ffns4bar=f"{theoryid}03",
            ffn04=f"{theoryid}04",
            ffns5til=f"{theoryid}05",
            ffns5bar=f"{theoryid}06",
            overwrite=overwrite,
            cfg=cfg,
        )

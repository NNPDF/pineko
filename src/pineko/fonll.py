"""Module to manage FONLL predictions."""

import copy
import dataclasses
import json
import logging
import tempfile
from pathlib import Path

import pineappl
import rich
import yaml

from . import configs

logger = logging.getLogger(__name__)

FNS_BASE_PTO = {"FONLL-A": 1, "FONLL-B": 1, "FONLL-C": 2, "FONLL-D": 2, "FONLL-E": 3}
"""Mapping between pertubative orders as in the theory card PTO and the FONLL scheme names.

The explict mapping is the following (evolution, massive parts, massless parts):
    * A: (1,1,1)
    * B: (1,2,1)
    * C: (2,2,2)
    * D: (2,3,2)
    * E: (3,3,3)
"""
MIXED_ORDER_FNS = ["FONLL-B", "FONLL-D"]
"""FONLL schemes with mixed orders."""
# Notice we rely on the order defined by the FONLLInfo class
FK_TO_DAMP = {
    "mc": ["ffn03", "ffns4til", "ffn04", "ffns5til"],
    "mb": ["ffn04", "ffns5til"],
}
FK_WITH_MINUS = ["ffn03", "ffn04"]  # asy terms should be subtracted, therefore the sign
"""FNS schemes to be subtracted during the FONLL procedure."""


class FONLLInfo:
    """Class containing all the information for FONLL predictions."""

    def __init__(
        self, ffns3, ffn03, ffns4til, ffns4bar, ffn04, ffns5til, ffns5bar
    ) -> None:
        """Initialize fonll info."""
        self.paths = {
            "ffns3": ffns3,
            "ffn03": ffn03,
            "ffns4til": ffns4til,
            "ffns4bar": ffns4bar,
            "ffn04": ffn04,
            "ffns5til": ffns5til,
            "ffns5bar": ffns5bar,
        }
        actually_existing_paths = [p for p, g in self.paths.items() if g is not None]
        for p in self.paths:
            if p not in actually_existing_paths:
                logger.warning(
                    "Warning! FK table for %s does not exist and thus is being skipped.",
                    p,
                )

    @property
    def fk_paths(self):
        """Returns the list of the FK table paths needed to produce FONLL predictions."""
        return {p: Path(self.paths[p]) for p, g in self.paths.items() if g is not None}

    @property
    def fks(self):
        """Returns the pineappl.Grid objects reading the paths provided by self.fk_paths."""
        # recall that FK tables are just a special grid
        return {fk: pineappl.grid.Grid.read(path) for fk, path in self.fk_paths.items()}

    @property
    def dataset_name(self):
        """Return the name of the underlaying dataset."""
        names = {self.fk_paths[p].name for p in self.fk_paths}
        if len(names) == 1:
            return names.pop()
        raise ValueError("Not all FK tables share the same name")

    @property
    def theorycard_no_fns_pto(self):
        """Return the common theory info between the different FONLL FK tables."""
        theorycards = [json.loads(self.fks[p].key_values()["theory"]) for p in self.fks]
        # Only these should differ
        for card in theorycards:
            del card["FNS"]
            del card["PTO"]
            card.pop("PTODIS", None)
            del card["NfFF"]
            del card["ID"]
            del card["FONLLParts"]
            del card["Comments"]
        if len(theorycards) > 1 and not all(
            [theorycards[0] == card for card in theorycards[1:]]
        ):
            raise ValueError("Theory cards are not compatible")
        return theorycards[0]

    @property
    def Q2grid(self):
        """The Q2grid of the (DIS) FK tables."""
        return self.fks[list(self.fks)[0]].bin_left(0)


def update_fk_theorycard(combined_fk, input_theorycard_path):
    """Update theorycard entries for the combined FK table.

    Update by reading the yamldb of the original theory.
    """
    with open(input_theorycard_path, encoding="utf-8") as f:
        final_theorycard = yaml.safe_load(f)
    theorycard = json.loads(combined_fk.key_values()["theory"])
    theorycard["FNS"] = final_theorycard["FNS"]
    theorycard["PTO"] = final_theorycard["PTO"]
    theorycard["NfFF"] = final_theorycard["NfFF"]
    theorycard["ID"] = final_theorycard["ID"]
    # Update the theorycard with the entries set above
    combined_fk.set_key_value("theory", str(theorycard))


def produce_dampings(theorycard_constituent_fks, fonll_info, damppowerc, damppowerb):
    """Return the damping factors for each of the relevant masses."""
    cmatching2 = (
        theorycard_constituent_fks["kcThr"] * theorycard_constituent_fks["mc"]
    ) ** 2
    bmatching2 = (
        theorycard_constituent_fks["kbThr"] * theorycard_constituent_fks["mb"]
    ) ** 2
    q2grid = fonll_info.Q2grid
    step_function_charm = cmatching2 < q2grid
    step_function_bottom = bmatching2 < q2grid
    damping_factor_charm = (1 - cmatching2 / q2grid) ** damppowerc
    damping_factor_bottom = (1 - bmatching2 / q2grid) ** damppowerb
    damping_factor_charm *= step_function_charm
    damping_factor_bottom *= step_function_bottom
    return {"mc": damping_factor_charm, "mb": damping_factor_bottom}


def combine(fk_dict, dampings=None):
    """Rescale, eventually using dampings, and combine the sub FK tables."""
    # pineappl does not support operating with two grids in memory:
    # https://github.com/NNPDF/pineappl/blob/8a672bef6d91b07a4edfdefbe4e30e4b1dd1f976/pineappl_py/src/grid.rs#L614-L617
    with tempfile.TemporaryDirectory() as tmpdirname:
        combined_fk = fk_dict[list(fk_dict)[0]]
        for fk in list(fk_dict)[1:]:
            tmpfile_path = Path(tmpdirname) / f"{fk}.pineappl.lz4"
            sign = -1 if fk in FK_WITH_MINUS else 1
            fk_dict[fk].scale(sign)
            if dampings is not None:
                for mass, fks in FK_TO_DAMP.items():
                    if fk in fks:
                        fk_dict[fk].scale_by_bin(dampings[mass])
            fk_dict[fk].write_lz4(tmpfile_path)
            combined_fk.merge_from_file(tmpfile_path)
    return combined_fk


def produce_combined_fk(
    ffns3,
    ffn03,
    ffns4til,
    ffns4bar,
    ffn04,
    ffns5til,
    ffns5bar,
    theoryid,
    damp=(0, None, None),
    cfg=None,
):
    """Combine the FONLL FK tables into one single FK table."""
    fonll_info = FONLLInfo(ffns3, ffn03, ffns4til, ffns4bar, ffn04, ffns5til, ffns5bar)
    theorycard_constituent_fks = fonll_info.theorycard_no_fns_pto
    fk_dict = fonll_info.fks
    dampings = (
        None
        if damp[0] == -1
        else produce_dampings(theorycard_constituent_fks, fonll_info, damp[1], damp[2])
    )
    combined_fk = combine(fk_dict, dampings=dampings)
    input_theorycard_path = (
        Path(configs.load(configs.detect(cfg))["paths"]["theory_cards"])
        / f"{theoryid}.yaml"
    )
    update_fk_theorycard(combined_fk, input_theorycard_path)
    # save final FONLL fktable
    fk_folder = Path(configs.load(configs.detect(cfg))["paths"]["fktables"]) / str(
        theoryid
    )
    fk_folder.mkdir(exist_ok=True)
    output_path_fk = fk_folder / fonll_info.dataset_name
    combined_fk.write_lz4(output_path_fk)


@dataclasses.dataclass
class SubTheoryConfig:
    """Single (sub-)theory configuration."""

    asy: bool
    nf: int
    parts: str
    delta_pto: int = 0

    @property
    def scheme(self):
        """Yadism scheme name."""
        return "FONLL-FFN" + ("0" if self.asy else "S")


FNS_CONFIG = [
    SubTheoryConfig(False, 3, "full", 1),
    SubTheoryConfig(True, 3, "full", 1),
    SubTheoryConfig(False, 4, "massless"),
    SubTheoryConfig(False, 4, "massive", 1),
    SubTheoryConfig(True, 4, "full", 1),
    SubTheoryConfig(False, 5, "massless"),
    SubTheoryConfig(False, 5, "massive", 1),
]
"""Mixed FONLL schemes."""


def collect_updates(fonll_fns):
    """Produce the different theory cards according to which FONLL is asked for."""
    updates = []
    is_mixed = fonll_fns in MIXED_ORDER_FNS
    base_pto = FNS_BASE_PTO[fonll_fns]
    cfgs = FNS_CONFIG
    for cfg in cfgs:
        po = int(base_pto) + (cfg.delta_pto if is_mixed else 0)
        updates.append(
            {
                "FNS": cfg.scheme,
                "NfFF": cfg.nf,
                "PTO": po,
                "FONLLParts": cfg.parts,
            }
        )
        # In a mixed FONLL scheme we only subract the resummed terms that are
        # present in the FFNS scheme at nf+1. E.g. for FONLL-B in FFN03 we
        # only subract up to NLL since there is no NNLL in FFNS4
        if fonll_fns in MIXED_ORDER_FNS and cfg.asy:
            updates[-1]["PTODIS"] = po
            updates[-1]["PTO"] = po - 1
    return updates


def dump_tcards(tcard, tcard_parent_path, theoryid):
    """Produce the seven FONLL theory cards from the original one.

    The produced theory cards are dumped in `tcard_parent_path` with names
    from '{theoryid}00.yaml' to '{theoryid}06.yaml'.
    """
    updates = collect_updates(tcard["FNS"])
    n_theory = len(updates)
    theorycards = [copy.deepcopy(tcard) for _ in range(n_theory)]
    paths_list = []
    for num, (theorycard, recipe) in enumerate(zip(theorycards, updates)):
        # update cards entries
        theorycard.update(recipe)
        theorycard["ID"] = int(f"{theoryid}0{num}")
        # save
        theorycard_path = tcard_parent_path / f'{theorycard["ID"]}.yaml'
        with open(theorycard_path, "w", encoding="UTF-8") as f:
            yaml.safe_dump(theorycard, f)
        paths_list.append(theorycard_path)
        rich.print(f"[green]Wrote theory card to {theorycard_path}")
    return paths_list

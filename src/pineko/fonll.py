"""Module to manage FONLL predictions."""

import copy
import json
import logging
import tempfile
from pathlib import Path

import numpy as np
import pineappl
import rich
import yaml

from . import configs

logger = logging.getLogger(__name__)


class FONLLInfo:
    """Class containing all the information for FONLL predictions."""

    def __init__(
        self, ffns3, ffn03, ffns4, ffns4til, ffns4bar, ffn04, ffns5, ffns5til, ffns5bar
    ) -> None:
        """Initialize fonll info."""
        self.ffns3 = ffns3
        self.ffn03 = ffn03
        self.ffns4 = ffns4
        self.ffns4til = ffns4til
        self.ffns4bar = ffns4bar
        self.ffn04 = ffn04
        self.ffns5 = ffns5
        self.ffns5til = ffns5til
        self.ffns5bar = ffns5bar

    @property
    def fk_paths(self):
        """Returns the list of the fk paths needed to produce FONLL predictions."""
        paths = {
            "ffns3": self.ffns3,
            "ffn03": self.ffn03,
            "ffns4": self.ffns4,
            "ffns4til": self.ffns4til,
            "ffns4bar": self.ffns4bar,
            "ffn04": self.ffn04,
            "ffns5": self.ffns5,
            "ffns5til": self.ffns5til,
            "ffns5bar": self.ffns5bar,
        }
        actually_existing_paths = [p for p in paths if paths[p] is not None]
        for p in paths:
            if p not in actually_existing_paths:
                logger.warning(
                    f"Warning! FK table for {p} does not exist and thus is being skipped."
                )
        return {p: Path(paths[p]) for p in actually_existing_paths}

    @property
    def fks(self):
        """Returns the pineappl.Grid objects reading the paths provided by self.fk_paths."""
        return {fk: pineappl.grid.Grid.read(path) for fk, path in self.fk_paths.items()}

    @property
    def dataset_name(self):
        """Return the name of the dataset given by the fktables name, if all the fktables have the same name."""
        names = {self.fk_paths[p].name for p in self.fk_paths}
        if len(names) == 1:
            return names.pop()
        raise ValueError("not all fktables have the same name")

    @property
    def theorycard_no_fns_pto(self):
        """Return the common theory info between the different FONLL FKs."""
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
        """Return the Q2grid of the fktables given by self.fks ."""
        obs = json.loads(self.fks[list(self.fks)[0]].key_values()["runcard"])[
            "observables"
        ]
        kins = list(obs.values())[
            0
        ]  # there is only a single observable because it's a dis fktable
        return np.array([i["Q2"] for i in kins])


# Notice we rely on the order defined by the FONLLInfo class
FK_TO_DAMP = {
    "mc": ["ffn03", "ffns4til", "ffn04", "ffns5til"],
    "mb": ["ffn04", "ffns5til"],
}
FK_WITH_MINUS = ["ffn03", "ffn04"]  # asy terms should be subtracted, therefore the sign


def produce_combined_fk(
    ffns3,
    ffn03,
    ffns4,
    ffns4til,
    ffns4bar,
    ffn04,
    ffns5,
    ffns5til,
    ffns5bar,
    theoryid,
    damp=(0, None),
    cfg=None,
):
    """Combine the FONLL FKs to produce one single final FONLL FK."""
    fonll_info = FONLLInfo(
        ffns3, ffn03, ffns4, ffns4til, ffns4bar, ffn04, ffns5, ffns5til, ffns5bar
    )
    theorycard_constituent_fks = fonll_info.theorycard_no_fns_pto
    fk_dict = fonll_info.fks
    if damp[0] == 0:
        # then there is no damping, not even Heaviside only
        combined_fk = fk_dict[list(fk_dict)[0]]
        # pineappl does not support operating with two grids in memory:
        # https://github.com/NNPDF/pineappl/blob/8a672bef6d91b07a4edfdefbe4e30e4b1dd1f976/pineappl_py/src/grid.rs#L614-L617
        with tempfile.TemporaryDirectory() as tmpdirname:
            for fk in list(fk_dict)[1:]:
                tmpfile_path = Path(tmpdirname) / f"{fk}.pineappl.lz4"
                sign = -1 if fk in FK_WITH_MINUS else 1
                fk_dict[fk].scale(sign)
                fk_dict[fk].write_lz4(tmpfile_path)
                combined_fk.merge_from_file(tmpfile_path)
    else:
        mc = theorycard_constituent_fks["mc"]
        mb = theorycard_constituent_fks["mb"]
        q2grid = fonll_info.Q2grid
        step_function_charm = mc**2 < q2grid
        step_function_bottom = mb**2 < q2grid
        damping_factor_charm = (1 - mc / q2grid) ** damp[1]
        damping_factor_bottom = (1 - mb / q2grid) ** damp[1]
        damping_factor_charm *= step_function_charm
        damping_factor_bottom *= step_function_bottom
        dampings = {"mc": damping_factor_charm, "mb": damping_factor_bottom}
        with tempfile.TemporaryDirectory() as tmpdirname:
            combined_fk = fk_dict[list(fk_dict)[0]]
            for fk in list(fk_dict)[1:]:
                tmpfile_path = Path(tmpdirname) / f"{fk}.pineappl.lz4"
                sign = -1 if fk in FK_WITH_MINUS else 1
                fk_dict[fk].scale(sign)
                for mass in FK_TO_DAMP:
                    if fk in FK_TO_DAMP[mass]:
                        fk_dict[fk].scale_by_bin(dampings[mass])
                fk_dict[fk].write_lz4(tmpfile_path)
                combined_fk.merge_from_file(tmpfile_path)

    # update theorycard entries for the combined fktable by reading the yamldb of the original theory
    input_theorycard_path = (
        Path(configs.load(configs.detect(cfg))["paths"]["theory_cards"])
        / f"{theoryid}.yaml"
    )
    with open(input_theorycard_path) as f:
        final_theorycard = yaml.safe_load(f)
    theorycard = json.loads(combined_fk.key_values()["theory"])
    theorycard["FNS"] = final_theorycard["FNS"]
    theorycard["PTO"] = final_theorycard["PTO"]
    theorycard["NfFF"] = final_theorycard["NfFF"]
    theorycard["ID"] = final_theorycard["ID"]
    # Update the theorycard with the entries set above
    combined_fk.set_key_value("theory", str(theorycard))

    # save final "fonll" fktable
    fk_folder = Path(configs.load(configs.detect(cfg))["paths"]["fktables"]) / str(
        theoryid
    )
    fk_folder.mkdir(exist_ok=True)
    output_path_fk = fk_folder / fonll_info.dataset_name
    combined_fk.write_lz4(output_path_fk)


FNS_BASE_PTO = {"FONLL-A": 1, "FONLL-B": 1, "FONLL-C": 2, "FONLL-D": 2, "FONLL-E": 3}
MIXED_ORDER_FNS = ["FONLL-B", "FONLL-D"]

# Mixed FONLL schemes
MIXED_FNS_LIST = [
    "FONLL-FFNS",
    "FONLL-FFN0",
    "FONLL-FFNS",
    "FONLL-FFNS",
    "FONLL-FFN0",
    "FONLL-FFNS",
    "FONLL-FFNS",
]
MIXED_NFFF_LIST = [3, 3, 4, 4, 4, 5, 5]
MIXED_PARTS_LIST = [
    "full",
    "full",
    "massless",
    "massive",
    "full",
    "massless",
    "massive",
]

# plain FONLL schemes
FNS_LIST = [
    "FONLL-FFNS",
    "FONLL-FFN0",
    "FONLL-FFNS",
    "FONLL-FFN0",
    "FONLL-FFNS",
]
NFFF_LIST = [3, 3, 4, 4, 5]
PARTS_LIST = ["full" for _ in range(5)]


def produce_ptos(fns, is_mixed_or_damp):
    """Produce the list of PTOs needed for the requested fns."""
    base_pto = FNS_BASE_PTO[fns]
    # mixed FONLL
    if fns in MIXED_ORDER_FNS:
        return [
            base_pto + 1,
            base_pto + 1,
            base_pto,
            base_pto + 1,
            base_pto + 1,
            base_pto,
            base_pto + 1,
        ]
    # plain FONLL with damping
    elif is_mixed_or_damp:
        return [base_pto for _ in range(7)]
    # plain FONLL without damping
    else:
        return [base_pto for _ in range(5)]


def produce_fonll_recipe(fonll_fns, damp):
    """Produce the different theory cards according to which FONLL is asked for."""
    fonll_recipe = []
    is_mixed_or_damp = fonll_fns in MIXED_ORDER_FNS or damp != 0
    fns_list = MIXED_FNS_LIST if is_mixed_or_damp else FNS_LIST
    nfff_list = MIXED_NFFF_LIST if is_mixed_or_damp else NFFF_LIST
    parts_list = MIXED_PARTS_LIST if is_mixed_or_damp else PARTS_LIST
    for fns, nfff, po, part in zip(
        fns_list, nfff_list, produce_ptos(fonll_fns, is_mixed_or_damp), parts_list
    ):
        fonll_recipe.append(
            {
                "FNS": fns,
                "NfFF": nfff,
                "PTO": po,
                "FONLLParts": part,
            }
        )
        # In a mixed FONLL scheme we only subract the resummed terms that are
        # present in the FFNS scheme at nf+1. E.g. for FONLL-B in FFN03 we
        # only subract up to NLL since there is no NNLL in FFNS4
        if fonll_fns in MIXED_ORDER_FNS and fns == "FONLL-FFN0":
            fonll_recipe[-1]["PTODIS"] = po
            fonll_recipe[-1]["PTO"] = po - 1
    return fonll_recipe


def produce_fonll_tcards(tcard, tcard_parent_path, theoryid):
    """Produce the seven fonll tcards from an original tcard and dump them in tcard_parent_path with names from '{theoryid}00.yaml' to '{theoryid}06.yaml'."""
    fonll_recipe = produce_fonll_recipe(tcard["FNS"], tcard["DAMP"])
    n_theory = len(fonll_recipe)
    theorycards = [copy.deepcopy(tcard) for _ in range(n_theory)]
    paths_list = []
    for num, (theorycard, recipe) in enumerate(zip(theorycards, fonll_recipe)):
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

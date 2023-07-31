"""Module to manage FONLL predictions."""

import copy
import json
import tempfile
from pathlib import Path

import numpy as np
import pineappl
import yaml

from . import configs


class FONLLInfo:
    """Class containing all the information for FONLL predictions."""

    def __init__(
        self, ffns3, ffn03, ffns4til, ffns4bar, ffn04, ffns5til, ffns5bar
    ) -> None:
        self.ffns3 = ffns3
        self.ffn03 = ffn03
        self.ffns4til = ffns4til
        self.ffns4bar = ffns4bar
        self.ffn04 = ffn04
        self.ffns5til = ffns5til
        self.ffns5bar = ffns5bar

    @property
    def fk_paths(self):
        """Returns the list of the fk paths needed to produce FONLL predictions."""
        paths = [self.ffns3, self.ffn03, self.ffns4til]
        if self.ffns4bar:
            paths = paths + [self.ffns4bar]
        if self.ffn04 and self.ffns5til:
            paths = paths + [self.ffn04, self.ffns5til]
            # It does not make sense to have ffns5bar without ffns5til
            if self.ffns5bar:
                paths = paths + [self.ffns5bar]
        return [Path(p) for p in paths]

    @property
    def fks(self):
        """Returns the pineappl.Grid objects reading the paths provided by self.fk_paths."""
        return [pineappl.grid.Grid.read(fk_path) for fk_path in self.fk_paths]

    @property
    def dataset_name(self):
        """Return the name of the dataset given by the fktables name, if all the fktables have the same name."""
        if len({p.name for p in self.fk_paths}) == 1:
            return self.fk_paths[0].name
        else:
            raise ValueError("not all fktables have the same name")

    @property
    def theorycard_no_fns_pto(self):
        """Return the common theory info between the different FONLL FKs."""
        theorycards = [json.loads(fk.key_values()["theory"]) for fk in self.fks]
        # Only these should differ
        for card in theorycards:
            del card["FNS"]
            del card["PTO"]
            del card["NfFF"]
            del card["ID"]
            del card["FONLLParts"]
        if not all([theorycards[0] == card in theorycards[1:]]):
            raise ValueError("theorycards not the same")
        return theorycards[0]

    @property
    def Q2grid(self):
        """Return the Q2grid of the fktables given by self.fks ."""
        aa = json.loads(self.fks[0].raw.key_values()["runcard"])["observables"]
        bb = list(aa.values())[
            0
        ]  # there is only a single obseravble because it's a dis fktable
        cc = np.array([i["Q2"] for i in bb])
        return cc


# Notice we rely on the order defined by the FONLLInfo class
FK_TO_DAMP = {"mc": [1, 2, 4, 5], "mb": [4, 5]}
FK_WITH_MINUS = [1, 4]  # asy terms should be subtracted, therefore the sign


def produce_combined_fk(
    ffns3, ffn03, ffns4til, ffns4bar, ffn04, ffns5til, ffns5bar, theoryid
):
    """Combine the FONLL FKs to produce one single final FONLL FK."""
    fonll_info = FONLLInfo(ffns3, ffn03, ffns4til, ffns4bar, ffn04, ffns5til, ffns5bar)

    theorycard_constituent_fks = fonll_info.theorycard_no_fns_pto
    if theorycard_constituent_fks["DAMP"] == 0:
        # then there is no damping, not even Heaviside only
        combined_fk = fonll_info.fks[0]
        with tempfile.TemporaryDirectory() as tmpdirname:
            for i, fk in enumerate(fonll_info.fks[1:]):
                tmpfile_path = Path(tmpdirname) / f"{i}.pineappl.lz4"
                sign = -1 if i + 1 in FK_WITH_MINUS else 1
                fk.scale(sign)
                fk.write_lz4(tmpfile_path)
                combined_fk.merge_from_file(tmpfile_path)
    else:
        mc = theorycard_constituent_fks["mc"]
        mb = theorycard_constituent_fks["mb"]
        q2grid = fonll_info.Q2grid
        step_function_charm = mc**2 < q2grid
        step_function_bottom = mb**2 < q2grid
        damping_factor_charm = (1 - q2grid / mc) ** theorycard_constituent_fks[
            "DAMPPOWER"
        ]
        damping_factor_bottom = (1 - q2grid / mb) ** theorycard_constituent_fks[
            "DAMPPOWER"
        ]
        damping_factor_charm *= step_function_charm
        damping_factor_bottom *= step_function_bottom
        dampings = {"mc": damping_factor_charm, "mb": damping_factor_bottom}
        for i, fk in enumerate(fonll_info.fks):
            for mass in FK_TO_DAMP:
                if i in FK_TO_DAMP[mass]:
                    fk.scale_by_bin(dampings[mass])
        # pineappl does not support operating with two grids in memory:
        # https://github.com/NNPDF/pineappl/blob/8a672bef6d91b07a4edfdefbe4e30e4b1dd1f976/pineappl_py/src/grid.rs#L614-L617
        with tempfile.TemporaryDirectory() as tmpdirname:
            combined_fk = fonll_info.fks[0]
            for i, fk in enumerate(fonll_info.fks[1:]):
                tmpfile_path = Path(tmpdirname) / f"{i}.pineappl.lz4"
                sign = (
                    -1 if i + 1 in FK_WITH_MINUS else 1
                )  # The i+1 is there because the first fk is not included in the loop
                fk.scale(sign)
                fk.write_lz4(tmpfile_path)
                combined_fk.merge_from_file(tmpfile_path)

    # update theorycard entries for the combined fktable by reading the yamldb of the original theory
    input_theorycard_path = (
        Path(configs.load(configs.detect())["paths"]["theory_cards"])
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
    fk_folder = Path(configs.load(configs.detect())["paths"]["fktables"]) / str(
        theoryid
    )
    fk_folder.mkdir(exist_ok=True)
    output_path_fk = fk_folder / fonll_info.dataset_name
    combined_fk.write_lz4(output_path_fk)


FNS_LIST = [
    "FONLL-FFNS",
    "FONLL-FFN0",
    "FONLL-FFNS",
    "FONLL-FFNS",
    "FONLL-FFN0",
    "FONLL-FFNS",
    "FONLL-FFNS",
]

NFFF_LIST = [3, 3, 4, 4, 4, 5, 5, 5]
PARTS_LIST = ["full", "full", "massless", "massive", "full", "massless", "massive"]
PTOS_DICT = {
    "FONLL-A": [1 for _ in range(7)],
    "FONLL-B": [2, 2, 1, 2, 2, 1, 2],
    "FONLL-C": [2 for _ in range(7)],
}


def produce_fonll_recipe(fns):
    """Produce the different theory cards according to which FONLL is asked for."""
    fonll_recipe = []
    for fns, nfff, po, part in zip(FNS_LIST, NFFF_LIST, PTOS_DICT[fns], PARTS_LIST):
        fonll_recipe.append(
            {
                "FNS": fns,
                "NfFF": nfff,
                "PTO": po,
                "FONLLParts": part,
            }
        )
    return fonll_recipe


def produce_fonll_tcards(tcard, tcard_parent_path, theoryid):
    """Produce the seven fonll tcards from an original tcard and dump them in tcard_parent_path with names from '{theoryid}00.yaml' to '{theoryid}06.yaml'."""
    theorycards = [copy.deepcopy(tcard) for _ in range(7)]
    fonll_recipe = produce_fonll_recipe(tcard["FNS"])
    for theorycard, recipe in zip(theorycards, fonll_recipe):
        theorycard.update(recipe)
    paths_list = [tcard_parent_path / f"{theoryid}0{num}.yaml" for num in range(7)]
    for newtcard, path in zip(theorycards, paths_list):
        with open(path, "w", encoding="UTF-8") as f:
            yaml.safe_dump(newtcard, f)
    return paths_list

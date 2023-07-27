import copy
import json
import tempfile
from pathlib import Path

import numpy as np
import pineappl
import yaml

from . import configs


class FONLLInfo:
    def __init__(self, ffns3, ffn03, ffns4, ffn04, ffns5) -> None:
        self.ffns3 = ffns3
        self.ffn03 = ffn03
        self.ffns4 = ffns4
        self.ffn04 = ffn04
        self.ffns5 = ffns5

    @property
    def fk_paths(self):
        always_needed = [self.ffns3, self.ffn03, self.ffns4]
        if self.ffn04 and self.ffns5:
            paths = always_needed + [self.ffn04, self.ffns5]
        else:
            paths = always_needed
        return [Path(p) for p in paths]

    @property
    def fks(self):
        return [pineappl.grid.Grid.read(fk_path) for fk_path in self.fk_paths]

    @property
    def dataset_name(self):
        if len({p.name for p in self.fk_paths}) == 1:
            return self.fk_paths[0].name
        else:
            raise ValueError("not all fktables have the same name")

    @property
    def theorycard_no_fns_pto(self):
        theorycards = [json.loads(fk.key_values()["theory"]) for fk in self.fks]
        # Only these should differ
        for card in theorycards:
            del card["FNS"]
            del card["PTO"]
            del card["NfFF"]
            del card["ID"]
        if not all([theorycards[0] == card in theorycards[1:]]):
            raise ValueError("theorycards not the same")
        return theorycards[0]

    @property
    def Q2grid(self):
        aa = json.loads(self.fks[0].raw.key_values()["runcard"])["observables"]
        bb = list(aa.values())[
            0
        ]  # there is only a single obseravble because it's a dis fktable
        cc = np.array([i["Q2"] for i in bb])
        return cc


def produce_combined_fk(ffns3, ffn03, ffns4, ffn04, ffns5, theoryid):
    fonll_info = FONLLInfo(ffns3, ffn03, ffns4, ffn04, ffns5)

    theorycard_constituent_fks = fonll_info.theorycard_no_fns_pto
    if theorycard_constituent_fks["DAMP"] == 0:
        # then there is no damping, not even Heaviside only
        combined_fk = fonll_info.fks[0]
        for fk_path in fonll_info.fk_paths[1:]:
            combined_fk.merge_from_file(fk_path)
    else:
        # TODO do also bottom
        mc = theorycard_constituent_fks["mc"]
        q2grid = fonll_info.Q2grid
        step_function = mc**2 < q2grid
        damping_factor = (1 - q2grid / mc) ** theorycard_constituent_fks["DAMP"]
        damping_factor *= step_function
        for i, fk in enumerate(fonll_info.fks[:-1]):  # we don't want to damp the last
            if i % 2 == 0:
                fk.scale_by_bin(damping_factor)
            else:
                fk.scale_by_bin(
                    -damping_factor
                )  # asy terms should be subtracted, therefore the sign
        # pineappl does not support operating with two grids in memory:
        # https://github.com/NNPDF/pineappl/blob/8a672bef6d91b07a4edfdefbe4e30e4b1dd1f976/pineappl_py/src/grid.rs#L614-L617
        with tempfile.TemporaryDirectory() as tmpdirname:
            combined_fk = fonll_info.fks[0]
            for i, fk in enumerate(fonll_info.fks[1:]):
                tmpfile_path = Path(tmpdirname) / f"{i}.pineappl.lz4"
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


# nf3, nf30, nf4til, nf4bar, nf40, nf5til, nf5bar
# 2,2,1,2,2,1,2
def produce_fonll_recipe(fns):
    """nf3, nf30, nf4til, nf4bar, nf40, nf5til, nf5bar
    2,2,1,2,2,1,2."""
    fonll_recipe = []
    if fns == "FONLL-A":
        pto = [1 for _ in range(7)]
    elif fns == "FONLL-C":
        pto = [2 for _ in range(7)]
    elif fns == "FONLL-B":
        pto = [2, 2, 1, 2, 2, 1, 2]
    FNS_list = [
        "FONLL-FFNS",
        "FONLL-FFN0",
        "FONLL-FFNS",
        "FONLL-FFNS",
        "FONLL-FFN0",
        "FONLL-FFNS",
        "FONLL-FFNS",
    ]
    NfFF_list = [3, 3, 4, 4, 4, 5, 5, 5]
    massiveonly_list = [False, False, False, True, False, False, True]
    masslessonly_list = [False, False, True, False, False, True, False]
    for fns, nfff, po, massiveonly, masslessonly in zip(
        FNS_list, NfFF_list, pto, massiveonly_list, masslessonly_list
    ):
        fonll_recipe.append(
            {
                "FNS": fns,
                "NfFF": nfff,
                "PTO": po,
                "massiveonly": massiveonly,
                "masslessonly": masslessonly,
            }
        )
    return fonll_recipe


def produce_fonll_tcards(tcard, tcard_parent_path):
    """Produce the six fonll tcards from an original tcard and dump them in tcard_parent_path
    with names from '1000.yaml' to '1005.yaml'"""
    theorycards = [copy.deepcopy(tcard) for _ in range(7)]
    fonll_recipe = produce_fonll_recipe(tcard["FNS"])
    for theorycard, recipe in zip(theorycards, fonll_recipe):
        theorycard.update(recipe)
    paths_list = [tcard_parent_path / f"100{num}.yaml" for num in range(7)]
    for newtcard, path in zip(theorycards, paths_list):
        with open(path, "w", encoding="UTF-8") as f:
            yaml.safe_dump(newtcard, f)

import pytest
import yaml

import pineko


@pytest.mark.parametrize("theoryid", [400, 208])
def benchmark_produce_fonll_tcards(tmp_path, test_files, test_configs, theoryid):
    tcard = pineko.theory_card.load(theoryid)
    tcard_paths_list = pineko.fonll.produce_fonll_tcards(tcard, tmp_path, theoryid)
    # Check they are correct
    theorycards = []
    for path in tcard_paths_list:
        with open(path, encoding="UTF-8") as f:
            theorycards.append(yaml.safe_load(f))
    for simFONLL_tcard, fns, nfff, po, part in zip(
        theorycards,
        pineko.fonll.FNS_LIST,
        pineko.fonll.NFFF_LIST,
        pineko.fonll.PTOS_DICT[tcard["FNS"]],
        pineko.fonll.PARTS_LIST,
    ):
        assert simFONLL_tcard["FNS"] == fns
        assert simFONLL_tcard["NfFF"] == nfff
        assert simFONLL_tcard["PTO"] == po
        assert simFONLL_tcard["FONLLParts"] == part

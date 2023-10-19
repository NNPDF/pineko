import numpy as np
import pytest
import yaml

import pineko


@pytest.mark.parametrize("theoryid", [400, 208])
def benchmark_produce_fonll_tcards(tmp_path, test_files, test_configs, theoryid):
    tcard = pineko.theory_card.load(theoryid)
    fonll_config = pineko.fonll.FonllSchemeConfig(tcard["FNS"], tcard["DAMP"])
    tcard_paths_list = pineko.fonll.produce_fonll_tcards(tcard, tmp_path, theoryid)
    # Check they are correct
    theorycards = []
    for path in tcard_paths_list:
        with open(path, encoding="UTF-8") as f:
            theorycards.append(yaml.safe_load(f))
    for num_fonll_tcard, fns, nfff, po, part in zip(
        theorycards,
        fonll_config.subfks_fns(),
        fonll_config.subfks_nfff(),
        fonll_config.subfks_ptos(),
        fonll_config.subfks_parts(),
    ):
        assert num_fonll_tcard["FNS"] == fns
        assert num_fonll_tcard["NfFF"] == int(nfff)
        assert num_fonll_tcard["PTO"] == po
        if fonll_config.is_mixed() and fns == "FONLL-FFN0":
            assert num_fonll_tcard["PTODIS"] == po + 1
        assert num_fonll_tcard["FONLLParts"] == part

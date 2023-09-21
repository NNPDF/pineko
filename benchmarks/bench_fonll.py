import pytest
import yaml

import pineko


@pytest.mark.parametrize("theoryid,is_mixed", [(400, False), (208, True)])
def benchmark_produce_fonll_tcards(
    tmp_path, test_files, test_configs, theoryid, is_mixed
):
    tcard = pineko.theory_card.load(theoryid)
    tcard_paths_list = pineko.fonll.produce_fonll_tcards(tcard, tmp_path, theoryid)
    # Check they are correct
    theorycards = []
    for path in tcard_paths_list:
        with open(path, encoding="UTF-8") as f:
            theorycards.append(yaml.safe_load(f))
    for simFONLL_tcard, fns, nfff, po, part in zip(
        theorycards,
        pineko.fonll.MIXED_FNS_LIST if is_mixed else pineko.fonll.FNS_LIST,
        pineko.fonll.MIXED_NFFF_LIST if is_mixed else pineko.fonll.NFFF_LIST,
        pineko.fonll.produce_ptos(tcard["FNS"], is_mixed),
        pineko.fonll.MIXED_PARTS_LIST if is_mixed else pineko.fonll.PARTS_LIST,
    ):
        assert simFONLL_tcard["FNS"] == fns
        assert simFONLL_tcard["NfFF"] == nfff
        assert simFONLL_tcard["PTO"] == po
        assert simFONLL_tcard["FONLLParts"] == part

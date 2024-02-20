import pytest
import yaml

import pineko


@pytest.mark.parametrize("theoryid,is_mixed", [(400, False), (208, True)])
def benchmark_produce_fonll_tcards(
    tmp_path, test_files, test_configs, theoryid, is_mixed
):
    tcard = pineko.theory_card.load(theoryid)
    tcard_paths_list = pineko.fonll.dump_tcards(tcard, tmp_path, theoryid)
    # Check they are correct
    theorycards = []
    for path in tcard_paths_list:
        with open(path, encoding="UTF-8") as f:
            theorycards.append(yaml.safe_load(f))
    base_pto = pineko.fonll.FNS_BASE_PTO[tcard["FNS"]]
    for num_fonll_tcard, cfg in zip(
        theorycards,
        pineko.fonll.FNS_CONFIG,
    ):
        po = int(base_pto) + (cfg.delta_pto if is_mixed else 0)
        assert num_fonll_tcard["FNS"] == cfg.scheme
        assert num_fonll_tcard["NfFF"] == int(cfg.nf)
        assert num_fonll_tcard["PTO"] == po - 1 if is_mixed and cfg.asy else po
        assert num_fonll_tcard["FONLLParts"] == cfg.parts

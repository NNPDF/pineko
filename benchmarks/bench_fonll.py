import pytest
import yaml

import pineko


def benchmark_produce_fonll_tcards(tmp_path, test_files, test_configs):
    tcard = pineko.theory_card.load(400)
    pineko.fonll.produce_fonll_tcards(tcard, tmp_path)
    # Check they are correct
    theorycards = []
    for num in range(7):
        with open(tmp_path / f"100{num}.yaml", encoding="UTF-8") as f:
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
        assert simFONLL_tcard["fonll-parts"] == part

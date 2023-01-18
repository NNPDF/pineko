import pytest

import pineko.evolve


def test_sv_scheme():
    wrong_tcard = {"XIF": 2.0, "fact_to_ren_scale_ratio": 0.5, "ModSV": "expanded"}
    wrong_tcard2 = {
        "XIF": 1.0,
        "fact_to_ren_scale_ratio": 0.5,
        "ModSV": "exponentiated",
    }
    schemeA_tcard = {
        "XIF": 2.0,
        "fact_to_ren_scale_ratio": 1.0,
        "ModSV": "exponentiated",
    }
    schemeB_tcard = {"XIF": 1.0, "fact_to_ren_scale_ratio": 0.5, "ModSV": "expanded"}
    schemeC_tcard = {"XIF": 2.0, "fact_to_ren_scale_ratio": 1.0, "ModSV": "None"}
    with pytest.raises(ValueError):
        pineko.evolve.sv_scheme(wrong_tcard)
    with pytest.raises(ValueError):
        pineko.evolve.sv_scheme(wrong_tcard2)
    assert pineko.evolve.sv_scheme(schemeA_tcard) == "A"
    assert pineko.evolve.sv_scheme(schemeB_tcard) == "B"
    assert pineko.evolve.sv_scheme(schemeC_tcard) == "C"

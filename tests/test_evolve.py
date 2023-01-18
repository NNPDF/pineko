import pytest

import pineko.evolve


def test_sv_scheme():
    wrong_tcard = {"XIF": 1.0, "ModSV": "expanded"}
    schemeA_tcard = {
        "XIF": 2.0,
        "ModSV": "exponentiated",
    }
    schemeB_tcard = {"XIF": 0.5, "ModSV": "expanded"}
    schemeC_tcard = {"XIF": 2.0, "ModSV": "None"}
    with pytest.raises(ValueError):
        pineko.evolve.sv_scheme(wrong_tcard)
    assert pineko.evolve.sv_scheme(schemeA_tcard) == "exponentiated"
    assert pineko.evolve.sv_scheme(schemeB_tcard) == "expanded"
    assert pineko.evolve.sv_scheme(schemeC_tcard) == "None"

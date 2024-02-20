import copy

import numpy as np
import pineappl
import pytest
import yaml
from banana.data.theories import default_card
from ekobox.cards import example

import pineko.evolve


def test_sv_scheme():
    wrong_tcard = {"XIF": 1.0, "ModSV": "expanded"}
    schemeA_tcard = {
        "XIF": 2.0,
        "ModSV": "exponentiated",
    }
    schemeB_tcard = {"XIF": 0.5, "ModSV": "expanded"}
    schemeC_tcard = {"XIF": 2.0, "ModSV": None}
    with pytest.raises(ValueError):
        pineko.evolve.sv_scheme(wrong_tcard)
    assert pineko.evolve.sv_scheme(schemeA_tcard) == "exponentiated"
    assert pineko.evolve.sv_scheme(schemeB_tcard) == "expanded"
    assert pineko.evolve.sv_scheme(schemeC_tcard) is None


class FakeEvolInfo:
    x1 = [0.1, 1.0]
    fac1 = np.array([10.0])


class FakePine:
    _evolve_info = FakeEvolInfo()

    def orders(self):
        return [pineappl.grid.Order(0, 0, 0, 0)]

    def lumi(self):
        return [[(21, 21, 1)]]

    def evolve_info(self, _):
        return self._evolve_info

    def key_values(self):
        return {}


def test_write_operator_card_q0(tmp_path):
    """Checks https://github.com/NNPDF/pineko/issues/146"""
    p = tmp_path / "q0.yaml"
    g = FakePine()
    # 1. defaults
    t = copy.deepcopy(default_card)
    o = copy.deepcopy(example.raw_operator())
    _xs, _mu2s = pineko.evolve.write_operator_card(g, o, p, t)
    with open(p, encoding="utf8") as f:
        oo = yaml.safe_load(f)
    np.testing.assert_allclose(oo["mu0"], t["Q0"])
    # 2. overwriting from theory side
    t["Q0"] = 10.0
    _xs, _mu2s = pineko.evolve.write_operator_card(g, o, p, t)
    with open(p, encoding="utf8") as f:
        oo = yaml.safe_load(f)
    np.testing.assert_allclose(oo["mu0"], t["Q0"])
    # 3. op template is ignored
    o["mu0"] = 11.0
    _xs, _mu2s = pineko.evolve.write_operator_card(g, o, p, t)
    with open(p, encoding="utf8") as f:
        oo = yaml.safe_load(f)
    np.testing.assert_allclose(oo["mu0"], t["Q0"])

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
        return [pineappl.boc.Order(0, 0, 0, 0, 0)]

    @property
    def convolutions(self):
        conv_type = pineappl.convolutions.ConvType(polarized=False, time_like=False)
        return [pineappl.convolutions.Conv(convolution_types=conv_type, pid=2212)]

    def channels(self):
        return [[([21, 21], 1)]]

    def evolve_info(self, _):
        return self._evolve_info

    @property
    def metadata(self):
        return {"convolution_particle_1": 2212, "convolution_particle_2": 11}


@pytest.fixture
def base_tcard():
    return {
        "FNS": "FONLL-C",
        "PTO": 1,
        "QED": 0,
        "XIF": 1.0,
        "Q0": 1.65,
        "nf0": 4,
        "ModSV": None,
        "MaxNfPdf": 5,
        "mc": 1.5,
        "mb": 4.5,
        "mt": 173.0,
        "kcThr": 1.0,
        "kbThr": 1.0,
        "ktThr": 1.0,
    }


def test_write_operator_card_evolution_methods(tmp_path, base_tcard):
    pine = FakePine()
    card_path = tmp_path / "opcard.yaml"

    # Missing ModEv
    tcard_no_modev = base_tcard.copy()
    with pytest.raises(ValueError, match="Evolution method not set in theory card"):
        pineko.evolve.write_operator_card(pine, card_path, tcard_no_modev, 4, True)

    # Unknown ModEv
    tcard_invalid = base_tcard.copy()
    tcard_invalid["ModEv"] = "FOO"
    with pytest.raises(ValueError, match="Unknown or unsupported evolution method"):
        pineko.evolve.write_operator_card(pine, card_path, tcard_invalid, 4, True)

    # EXA without IterEv
    tcard_exa_no_iter = base_tcard.copy()
    tcard_exa_no_iter["ModEv"] = "EXA"
    with pytest.raises(
        ValueError, match="EXA used but IterEv not found in the theory card"
    ):
        pineko.evolve.write_operator_card(pine, card_path, tcard_exa_no_iter, 4, True)

    # EXA with IterEv
    tcard_exa = base_tcard.copy()
    tcard_exa["ModEv"] = "EXA"
    tcard_exa["IterEv"] = 10
    xgrid, q2grid = pineko.evolve.write_operator_card(
        pine, card_path, tcard_exa, 4, True
    )
    assert len(xgrid) == 50
    assert len(q2grid) == 1

    # TRN with IterEv > 1 raises error (issue #176)
    tcard_trn_multi_iter = base_tcard.copy()
    tcard_trn_multi_iter["ModEv"] = "TRN"
    tcard_trn_multi_iter["IterEv"] = 2
    with pytest.raises(
        ValueError,
        match="Truncated evolution method does not support number of iterations > 1",
    ):
        pineko.evolve.write_operator_card(
            pine, card_path, tcard_trn_multi_iter, 4, True
        )

    # TRN with IterEv == 1 succeeds
    tcard_trn_valid = base_tcard.copy()
    tcard_trn_valid["ModEv"] = "TRN"
    tcard_trn_valid["IterEv"] = 1
    xgrid, q2grid = pineko.evolve.write_operator_card(
        pine, card_path, tcard_trn_valid, 4, True
    )
    assert len(xgrid) == 50
    assert len(q2grid) == 1

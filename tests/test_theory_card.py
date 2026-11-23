import pytest

import pineko.theory_card


def test_construct_assumptions():
    fake_t_card = {
        "Q0": 1.65,
        "kcThr": 1.0,
        "kbThr": 1.0,
        "ktThr": 1.0,
        "mc": 2.0,
        "mb": 3.0,
        "mt": 50.0,
        "IC": 1,
    }
    assert pineko.theory_card.construct_assumptions(fake_t_card) == "Nf4Ind"

    fake_t_card["IC"] = 0
    assert pineko.theory_card.construct_assumptions(fake_t_card) == "Nf3Ind"


def test_qed_running_alpha():
    tcard = {"alphaqed": 1 / 132.1, "MZ": 91.188, "Qref": 91.188}
    # without alpha_qed_running_mz, alphaqed is the running coupling (as in NNPDF4.0)
    assert pineko.theory_card.qed_running_alpha(tcard) == 1 / 132.1
    tcard["alpha_qed_running_mz"] = 1 / 128.94
    assert pineko.theory_card.qed_running_alpha(tcard) == 1 / 128.94
    tcard["Qref"] = 91.2
    with pytest.raises(ValueError):
        pineko.theory_card.qed_running_alpha(tcard)

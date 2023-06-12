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
    assert pineko.theory_card.construct_assumptions(fake_t_card) == "Nf4Sym"

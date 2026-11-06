import copy
import json
import pathlib

import pytest
from banana.data.theories import default_card

import pineko


def test_FONLLInfo():
    full_list = [
        "ffns3.pineappl.lz4",
        "ffn03.pineappl.lz4",
        "ffns4til.pineappl.lz4",
        "ffns4bar.pineappl.lz4",
        "ffn04.pineappl.lz4",
        "ffns5til.pineappl.lz4",
        "ffns5bar.pineappl.lz4",
    ]
    fullfonll_fake_info = pineko.fonll.FONLLInfo(*full_list)
    wrongfonll_fake_info = pineko.fonll.FONLLInfo(
        full_list[0],
        full_list[1],
        None,
        full_list[3],
        full_list[4],
        None,
        None,
    )
    partialfonll_fake_info = pineko.fonll.FONLLInfo(
        full_list[0], full_list[1], full_list[2], full_list[3], None, None, None
    )
    name_list = [
        "ffns3",
        "ffn03",
        "ffns4zeromass",
        "ffns4massive",
        "ffn04",
        "ffns5zeromass",
        "ffns5massive",
    ]
    assert fullfonll_fake_info.fk_paths == {
        name: pathlib.Path(fk) for name, fk in zip(name_list, full_list)
    }
    assert wrongfonll_fake_info.fk_paths == {
        name: pathlib.Path(fk)
        for name, fk in zip(
            name_list[:2] + name_list[3:5],
            full_list[:2] + full_list[3:5],
        )
    }
    assert partialfonll_fake_info.fk_paths == {
        name: pathlib.Path(fk)
        for name, fk in zip(name_list[:4], full_list[:4])
        if fk is not None
    }


class FakeGrid:
    def __init__(self, metadata=None):
        self.kv = dict(metadata) if metadata is not None else {}

    @property
    def metadata(self):
        return self.kv

    def set_metadata(self, k, v):
        self.kv[k] = v


def test_update_fk_theorycard(tmp_path):
    # prepare base card
    p = tmp_path / "blub.yaml"
    base_tc = copy.deepcopy(default_card)
    base_tc["PTO"] = 2
    p.write_text(json.dumps(base_tc))
    # fake grid
    fg = FakeGrid()
    fk_tc = copy.deepcopy(default_card)
    fk_tc["PTO"] = 1
    fg.set_metadata("theory", json.dumps(fk_tc))
    # run the update
    pineko.fonll.update_fk_theorycard(fg, p)
    # check it actually worked
    new_tc = json.loads(fg.metadata["theory"])
    assert new_tc["PTO"] == base_tc["PTO"]


def test_theorycard_no_fns_pto_compatible(monkeypatch):
    """Test that theory cards differing only in ignored keys (FNS, PTO, XIA, etc.) are compatible."""
    card1 = copy.deepcopy(default_card)
    card1.update(
        {
            "FNS": "FONLL-B",
            "PTO": 2,
            "ID": 101,
            "PTODIS": 2,
            "NfFF": 5,
            "FONLLParts": "massive",
            "Comments": "card 1",
            "XIA": 1.0,
        }
    )

    card2 = copy.deepcopy(default_card)
    card2.update(
        {
            "FNS": "FONLL-A",
            "PTO": 1,
            "ID": 102,
            "PTODIS": 1,
            "NfFF": 4,
            "FONLLParts": "massless",
            "Comments": "card 2",
            "XIA": 2.0,
        }
    )

    card3 = copy.deepcopy(default_card)
    card3.update(
        {
            "FNS": "FONLL-C",
            "PTO": 3,
        }
    )
    # card3 does not have XIA set (issue #232 / PR #232)
    card3.pop("XIA", None)

    grid1 = FakeGrid(metadata={"theory": json.dumps(card1)})
    grid2 = FakeGrid(metadata={"theory": json.dumps(card2)})
    grid3 = FakeGrid(metadata={"theory": json.dumps(card3)})

    fonll_info = pineko.fonll.FONLLInfo("a", "b", "c", None, None, None, None)
    fake_fks = {"ffns3": grid1, "ffn03": grid2, "ffns4zeromass": grid3}
    monkeypatch.setattr(pineko.fonll.FONLLInfo, "fks", property(lambda self: fake_fks))

    result = fonll_info.theorycard_no_fns_pto
    assert result["Q0"] == default_card["Q0"]
    assert result["FNS"] == "FONLL-B"
    assert result["PTO"] == 2


def test_theorycard_no_fns_pto_incompatible(monkeypatch):
    """Test that differing keys outside dont_check raise ValueError naming the differing keys."""
    card1 = copy.deepcopy(default_card)
    card2 = copy.deepcopy(default_card)
    card2["Q0"] = 99.0
    card2["ModEv"] = "EXA" if default_card.get("ModEv") != "EXA" else "TRN"

    grid1 = FakeGrid(metadata={"theory": json.dumps(card1)})
    grid2 = FakeGrid(metadata={"theory": json.dumps(card2)})

    fonll_info = pineko.fonll.FONLLInfo("a", "b", None, None, None, None, None)
    fake_fks = {"ffns3": grid1, "ffn03": grid2}
    monkeypatch.setattr(pineko.fonll.FONLLInfo, "fks", property(lambda self: fake_fks))

    with pytest.raises(
        ValueError,
        match="The following keys differ between different FONLL theory cards:",
    ) as exc_info:
        _ = fonll_info.theorycard_no_fns_pto

    err_msg = str(exc_info.value)
    assert "Q0" in err_msg
    assert "ModEv" in err_msg


def test_theorycard_no_fns_pto_single_card(monkeypatch):
    """Test that a single theory card returns without comparison errors."""
    card1 = copy.deepcopy(default_card)
    grid1 = FakeGrid(metadata={"theory": json.dumps(card1)})

    fonll_info = pineko.fonll.FONLLInfo("a", None, None, None, None, None, None)
    monkeypatch.setattr(
        pineko.fonll.FONLLInfo, "fks", property(lambda self: {"ffns3": grid1})
    )

    result = fonll_info.theorycard_no_fns_pto
    assert result["Q0"] == default_card["Q0"]


def test_json_theory_read():
    """Test _json_theory_read with standard json and python repr formats."""
    # Standard JSON format
    sample = {"Q0": 1.65, "PTO": 1}
    assert pineko.fonll._json_theory_read(json.dumps(sample)) == sample

    # Malformed / python string format with single quotes and True/False
    raw_str = "{'Q0': 1.65, 'PTO': 1, 'EScale': True}"
    expected = {"Q0": 1.65, "PTO": 1, "EScale": True}
    assert pineko.fonll._json_theory_read(raw_str) == expected

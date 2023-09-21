import pathlib

import pytest

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
        full_list[0], full_list[1], full_list[2], full_list[3], None, None, full_list[6]
    )
    partialfonll_fake_info = pineko.fonll.FONLLInfo(
        full_list[0], full_list[1], full_list[2], None, None, None, None
    )
    name_list = [
        "ffns3",
        "ffn03",
        "ffns4til",
        "ffns4bar",
        "ffn04",
        "ffns5til",
        "ffns5bar",
    ]
    assert fullfonll_fake_info.fk_paths == {
        name: pathlib.Path(fk) for name, fk in zip(name_list, full_list)
    }
    assert wrongfonll_fake_info.fk_paths == {
        name: pathlib.Path(fk)
        for name, fk in zip(
            name_list[:4] + [name_list[-1]], full_list[:4] + [full_list[-1]]
        )
    }
    assert partialfonll_fake_info.fk_paths == {
        name: pathlib.Path(fk)
        for name, fk in zip(name_list[:3], full_list[:3])
        if fk is not None
    }
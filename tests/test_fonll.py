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
    assert fullfonll_fake_info.fk_paths == [pathlib.Path(fk) for fk in full_list]
    # In this case it ignores the ffns5bar fk
    assert wrongfonll_fake_info.fk_paths == [pathlib.Path(fk) for fk in full_list[:4]]
    assert partialfonll_fake_info.fk_paths == [pathlib.Path(fk) for fk in full_list[:3]]

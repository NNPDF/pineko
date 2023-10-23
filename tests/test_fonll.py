import pathlib

import pineko


def test_FONLLInfo():
    full_list = [
        "ffns3.pineappl.lz4",
        "ffn03.pineappl.lz4",
        "ffns4.pineappl.lz4",
        "ffns4til.pineappl.lz4",
        "ffns4bar.pineappl.lz4",
        "ffn04.pineappl.lz4",
        "ffns5.pineappl.lz4",
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
        None,
        full_list[8],
    )
    partialfonll_fake_info = pineko.fonll.FONLLInfo(
        full_list[0], full_list[1], None, full_list[3], None, None, None, None, None
    )
    name_list = [
        "ffns3",
        "ffn03",
        "ffns4",
        "ffns4til",
        "ffns4bar",
        "ffn04",
        "ffns5",
        "ffns5til",
        "ffns5bar",
    ]
    assert fullfonll_fake_info.fk_paths == {
        name: pathlib.Path(fk) for name, fk in zip(name_list, full_list)
    }
    assert wrongfonll_fake_info.fk_paths == {
        name: pathlib.Path(fk)
        for name, fk in zip(
            name_list[:2] + name_list[3:5] + [name_list[-1]],
            full_list[:2] + full_list[3:5] + [full_list[-1]],
        )
    }
    assert partialfonll_fake_info.fk_paths == {
        name: pathlib.Path(fk)
        for name, fk in zip(
            name_list[:2] + name_list[3:4], full_list[:2] + full_list[3:4]
        )
        if fk is not None
    }

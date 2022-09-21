# -*- coding: utf-8 -*-
import pathlib

import pineko

test_files = pathlib.Path(__file__).parents[0] / "data_files/"


def benchmark_load():
    base_configs = pineko.configs.load(test_files)
    pineko.configs.configs = pineko.configs.defaults(base_configs)
    tcard = pineko.theory_card.load(208)
    assert tcard["MP"] == 0.938
    assert tcard["PTO"] == 1


def benchmark_construct_assumption():
    base_configs = pineko.configs.load(test_files)
    pineko.configs.configs = pineko.configs.defaults(base_configs)
    tcard = pineko.theory_card.load(208)
    ass_ash = pineko.theory_card.construct_assumptions(tcard)
    assert ass_ash == "Nf4Ind"

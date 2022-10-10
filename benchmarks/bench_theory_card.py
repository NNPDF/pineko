# -*- coding: utf-8 -*-
import pathlib

import pineko


def benchmark_load(test_files):
    base_configs = pineko.configs.load(test_files)
    pineko.configs.configs = pineko.configs.defaults(base_configs)
    tcard = pineko.theory_card.load(208)
    assert tcard["MP"] == 0.938
    assert tcard["PTO"] == 1


def benchmark_construct_assumption(test_files):
    base_configs = pineko.configs.load(test_files)
    pineko.configs.configs = pineko.configs.defaults(base_configs)
    tcard = pineko.theory_card.load(208)
    ass_ash = pineko.theory_card.construct_assumptions(tcard)
    assert ass_ash == "Nf4Ind"

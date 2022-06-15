# -*- coding: utf-8 -*-
import pathlib

import pytest

import pineko

test_files = pathlib.Path(__file__).parents[0] / "test_files/"


def test_load():
    base_configs = pineko.configs.load(test_files)
    pineko.configs.configs = pineko.configs.defaults(base_configs)
    tcard = pineko.theory_card.load(208)
    assert tcard["MP"] == 0.938
    assert tcard["PTO"] == 1


def test_construct_assumption():
    base_configs = pineko.configs.load(test_files)
    pineko.configs.configs = pineko.configs.defaults(base_configs)
    tcard = pineko.theory_card.load(208)
    ass_ash = pineko.theory_card.construct_assumption(tcard)
    assert ass_ash == "Nf4Ind"

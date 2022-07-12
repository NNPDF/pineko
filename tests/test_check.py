# -*- coding: utf-8 -*-
import pathlib

import eko
import numpy as np
import pineappl
import pytest

import pineko.check


def test_is_fonll_b():
    fns = "FONLL-B"
    lumi = [[(1, 11, 3, 4), (3, 11, 5, 6)], [(9, 11, 0, 3), (8, 11, -2, -1)]]
    assert pineko.check.is_fonll_b(fns, lumi) is True
    lumi.append([(1, 11, 2, 3), (2, 4, 5, 6)])
    assert pineko.check.is_fonll_b(fns, lumi) is False
    lumi.pop(-1)
    fns = "FONLL-C"
    assert pineko.check.is_fonll_b(fns, lumi) is False

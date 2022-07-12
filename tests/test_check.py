# -*- coding: utf-8 -*-
import pathlib

import eko
import numpy as np
import pineappl
import pytest

import pineko.check

test_files = pathlib.Path(__file__).parents[0] / "test_files/"


def test_in1d():
    to_check = np.array([0.3])
    against_this = np.array(
        [1, 2, 0.3, 90, 67, 10.0e-10, 0.00002, 12567, 1729291, 10.0e-7]
    )
    checked = pineko.check.in1d(to_check, against_this)
    assert checked == np.array([True])


def test_check_grid_and_eko_compatible():
    grid = pineappl.grid.Grid.read(
        test_files / "data/grids/208/HERA_CC_318GEV_EM_SIGMARED.pineappl.lz4"
    )
    wrong_grid = pineappl.grid.Grid.read(
        test_files / "data/grids/208/NUTEV_CC_NU_FE_SIGMARED.pineappl.lz4"
    )
    ekoop = eko.output.Output.load_tar(
        test_files / "data/ekos/208/HERA_CC_318GEV_EM_SIGMARED.tar"
    )
    with pytest.raises(ValueError):
        pineko.check.check_grid_and_eko_compatible(wrong_grid, ekoop)
    pineko.check.check_grid_and_eko_compatible(grid, ekoop)

def test_is_fonll_b():
    fns = "FONLL-B"
    lumi = [[(1, 11, 3, 4), (3, 11, 5, 6)], [(9, 11, 0, 3), (8, 11, -2, -1)]]
    assert pineko.check.is_fonll_b(fns, lumi) is True
    lumi.append([(1, 11, 2, 3), (2, 4, 5, 6)])
    assert pineko.check.is_fonll_b(fns, lumi) is False
    lumi.pop(-1)
    fns = "FONLL-C"
    assert pineko.check.is_fonll_b(fns, lumi) is False

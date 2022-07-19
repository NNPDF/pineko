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
    lumi_first = [[(-12, 1, 2.0), (-13, 1, 5.0)]]
    lumi_second = [[(1, 11, 1.0), (3, 11, 5.0)]]
    assert pineko.check.is_fonll_b(fns, lumi_first) is True
    assert pineko.check.is_fonll_b(fns, lumi_second) is True
    lumi_crazy = [[(1, 1, 4.0), (2, 11, 3.0)]]
    assert pineko.check.is_fonll_b(fns, lumi_crazy) is False
    fns = "FONLL-C"
    assert pineko.check.is_fonll_b(fns, lumi_first) is False
    assert pineko.check.is_fonll_b(fns, lumi_second) is False
    assert pineko.check.is_fonll_b(fns, lumi_crazy) is False

class Fake_grid:
    def __init__(self, order_list):
        self.orderlist = order_list

    def orders(self):
        return self.orderlist


class Order:
    def __init__(self, order_tup):
        self.orders = order_tup

    def as_tuple(self):
        return self.orders


def test_contains_fact():
    first_order = Order((0, 0, 0, 0))
    second_order = Order((1, 1, 0, 0))
    third_order = Order((0, 0, 1, 1))
    order_list = [first_order, second_order, third_order]
    mygrid = Fake_grid(order_list)
    assert pineko.check.contains_fact(mygrid) is None
    order_list.pop(-1)
    mygrid_nofact = Fake_grid(order_list)
    with pytest.raises(ValueError):
        pineko.check.contains_fact(mygrid_nofact)


def test_contains_ren():
    first_order = Order((0, 0, 0, 0))
    second_order = Order((1, 1, 0, 0))
    third_order = Order((0, 0, 1, 1))
    order_list = [first_order, second_order, third_order]
    mygrid = Fake_grid(order_list)
    assert pineko.check.contains_ren(mygrid) is None
    order_list.pop(-1)
    mygrid_nofact = Fake_grid(order_list)
    with pytest.raises(ValueError):
        pineko.check.contains_ren(mygrid_nofact)

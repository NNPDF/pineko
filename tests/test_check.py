# -*- coding: utf-8 -*-
import pathlib

import eko
import numpy as np
import pineappl
import pytest

import pineko.check


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


def test_is_fonll_b():
    fns = "FONLL-B"
    lumi = [[(1, 11, 1.0), (3, 11, 5.0)]]
    assert pineko.check.is_fonll_b(fns, lumi) is True
    lumi.append([(-12, 1, 2.0), (-13, 1, 5.0)])
    assert pineko.check.is_fonll_b(fns, lumi) is True
    lumi.append([(1, 1, 4.0), (2, 11, 3.0)])
    assert pineko.check.is_fonll_b(fns, lumi) is False
    lumi.pop(-1)
    fns = "FONLL-C"
    assert pineko.check.is_fonll_b(fns, lumi) is False

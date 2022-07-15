# -*- coding: utf-8 -*-
import pathlib

import eko
import numpy as np
import pineappl
import pytest
from pineappl.pineappl import PyOrder

import pineko.check


class Fake_grid:
    def __init__(self, order_list):
        self.orderlist = order_list

    def orders(self):
        return self.orderlist


class Order:
    def __init__(self, order_tup):
        self.orders = order_tup
        self._raw = PyOrder(order_tup[0], order_tup[1], order_tup[2], order_tup[3])

    def as_tuple(self):
        return self.orders


def test_contains_fact():
    max_as = 2
    max_al = 1
    first_order = Order((0, 0, 0, 0))
    second_order = Order((1, 0, 0, 0))
    third_order = Order((1, 0, 0, 1))
    order_list = [first_order, second_order, third_order]
    mygrid = Fake_grid(order_list)
    assert tuple(pineko.check.contains_fact(mygrid, max_as, max_al)) == (True, True)
    order_list.pop(-1)
    mygrid_nofact = Fake_grid(order_list)
    assert tuple(pineko.check.contains_fact(mygrid_nofact, max_as, max_al)) == (
        False,
        True,
    )
    assert tuple(pineko.check.contains_fact(mygrid_nofact, max_as - 1, max_al)) == (
        True,
        True,
    )
    order_list.pop(-1)
    mygrid_LO = Fake_grid(order_list)
    assert tuple(pineko.check.contains_fact(mygrid_LO, max_as, max_al)) == (True, True)


def test_contains_ren():
    max_as = 3
    max_al = 0
    first_order = Order((0, 0, 0, 0))
    second_order = Order((1, 0, 0, 0))
    third_order = Order((2, 0, 1, 0))
    order_list = [first_order, second_order, third_order]
    mygrid = Fake_grid(order_list)
    assert tuple(pineko.check.contains_ren(mygrid, max_as, max_al)) == (True, True)
    order_list.pop(-1)
    mygrid_new = Fake_grid(order_list)
    assert tuple(pineko.check.contains_ren(mygrid_new, max_as, max_al)) == (True, True)
    order_list.append(Order((2, 0, 0, 0)))
    mygrid_noren = Fake_grid(order_list)
    assert tuple(pineko.check.contains_ren(mygrid_noren, max_as, max_al)) == (
        False,
        True,
    )
    assert tuple(pineko.check.contains_ren(mygrid_noren, max_as - 1, max_al)) == (
        True,
        True,
    )
    order_list.pop(0)
    mygrid_noren = Fake_grid(order_list)
    assert tuple(pineko.check.contains_ren(mygrid_noren, max_as, max_al)) == (
        False,
        True,
    )


def test_is_fonll_b():
    fns = "FONLL-B"
    lumi = [[(1, 11, 3, 4), (3, 11, 5, 6)], [(9, 11, 0, 3), (-12, 3, -2, -1)]]
    assert pineko.check.is_fonll_b(fns, lumi) is True
    lumi.append([(1, 11, 2, 3), (2, 4, 5, 6)])
    assert pineko.check.is_fonll_b(fns, lumi) is False
    lumi.pop(-1)
    fns = "FONLL-C"
    assert pineko.check.is_fonll_b(fns, lumi) is False

import numpy as np
import pineappl

import pineko.check


def test_in1d():
    to_check = np.array([0.3])
    against_this = np.array(
        [1, 2, 0.3, 90, 67, 10.0e-10, 0.00002, 12567, 1729291, 10.0e-7]
    )
    checked = pineko.check.in1d(to_check, against_this)
    assert checked == np.array([True])


def test_is_dis():
    initial_conv_type = pineappl.convolutions.ConvType(polarized=True, time_like=False)
    final_conv_type = pineappl.convolutions.ConvType(polarized=False, time_like=True)
    dis_convolution = [pineappl.convolutions.Conv(initial_conv_type, 2212)]
    timelike_convolution = [pineappl.convolutions.Conv(final_conv_type, 211)]
    hadronic_convolution = [
        pineappl.convolutions.Conv(initial_conv_type, 2212),
        pineappl.convolutions.Conv(initial_conv_type, 2212),
    ]
    assert pineko.check.is_dis(dis_convolution) is True
    assert pineko.check.is_dis(timelike_convolution) is False
    assert pineko.check.is_dis(hadronic_convolution) is False


def test_is_fonll_mixed():
    unpol_conv_type = pineappl.convolutions.ConvType(polarized=False, time_like=False)
    pol_conv_type = pineappl.convolutions.ConvType(polarized=True, time_like=False)
    final_conv_type = pineappl.convolutions.ConvType(polarized=False, time_like=True)

    fns = "FONLL-B"
    convolutions_first = [pineappl.convolutions.Conv(unpol_conv_type, 2212)]
    convolutions_second = [pineappl.convolutions.Conv(pol_conv_type, 2212)]
    convolutions_third = [pineappl.convolutions.Conv(final_conv_type, 211)]
    assert pineko.check.is_fonll_mixed(fns, convolutions_first) is True
    assert pineko.check.is_fonll_mixed(fns, convolutions_second) is True
    assert pineko.check.is_fonll_mixed(fns, convolutions_third) is False
    convolutions_crazy = [
        pineappl.convolutions.Conv(unpol_conv_type, 2212),
        pineappl.convolutions.Conv(pol_conv_type, 2212),
    ]
    assert pineko.check.is_fonll_mixed(fns, convolutions_crazy) is False
    fns = "FONLL-C"
    assert pineko.check.is_fonll_mixed(fns, convolutions_first) is False
    assert pineko.check.is_fonll_mixed(fns, convolutions_second) is False
    assert pineko.check.is_fonll_mixed(fns, convolutions_crazy) is False
    fns = "FONLL-D"
    assert pineko.check.is_fonll_mixed(fns, convolutions_first) is True
    assert pineko.check.is_fonll_mixed(fns, convolutions_second) is True
    assert pineko.check.is_fonll_mixed(fns, convolutions_crazy) is False


def test_is_num_fonll():
    num_fonll_FNS = "FONLL-FFN0"
    non_num_fonll_FNS = "FONLL-B"
    assert pineko.check.is_num_fonll(num_fonll_FNS) is True
    assert pineko.check.is_num_fonll(non_num_fonll_FNS) is False


class Fake_grid:
    def __init__(self, order_list):
        self.orderlist = order_list

    def orders(self):
        return [order._raw for order in self.orderlist]


class Order:
    def __init__(self, order_tup):
        self.orders = order_tup
        self._raw = pineappl.boc.Order(*order_tup)

    def as_tuple(self):
        return self.orders


def test_contains_fact():
    max_as = 2
    max_al = 1
    first_order = Order((0, 0, 0, 0, 0))
    second_order = Order((1, 0, 0, 0, 0))
    third_order = Order((1, 0, 0, 1, 0))
    order_list = [first_order, second_order, third_order]
    mygrid = Fake_grid(order_list)
    checkres, max_as_effective = pineko.check.contains_sv(
        mygrid, max_as, max_al, pineko.check.Scale.FACT
    )
    assert checkres is pineko.check.AvailableAtMax.BOTH
    assert max_as_effective == max_as
    order_list.pop(-1)
    mygrid_nofact = Fake_grid(order_list)
    checkres, max_as_effective = pineko.check.contains_sv(
        mygrid_nofact, max_as, max_al, pineko.check.Scale.FACT
    )
    assert checkres is pineko.check.AvailableAtMax.CENTRAL
    assert max_as_effective == max_as
    checkres, max_as_effective = pineko.check.contains_sv(
        mygrid_nofact, max_as - 1, max_al, pineko.check.Scale.FACT
    )
    assert checkres is pineko.check.AvailableAtMax.BOTH
    assert max_as_effective == max_as - 1
    order_list.pop(-1)
    mygrid_LO = Fake_grid(order_list)
    checkres, max_as_effective = pineko.check.contains_sv(
        mygrid_LO, max_as, max_al, pineko.check.Scale.FACT
    )
    assert checkres is pineko.check.AvailableAtMax.BOTH
    assert max_as_effective == max_as - 1
    order_list = [first_order, third_order]
    mygrid = Fake_grid(order_list)
    checkres, max_as_effective = pineko.check.contains_sv(
        mygrid, max_as, max_al, pineko.check.Scale.FACT
    )
    assert checkres is pineko.check.AvailableAtMax.SCVAR
    assert max_as_effective == max_as


def test_contains_ren():
    max_as = 3
    max_al = 0
    first_order = Order((0, 0, 0, 0, 0))
    second_order = Order((1, 0, 0, 0, 0))
    third_order = Order((2, 0, 1, 0, 0))
    order_list = [first_order, second_order, third_order]
    mygrid = Fake_grid(order_list)
    checkres, max_as_effective = pineko.check.contains_sv(
        mygrid, max_as, max_al, pineko.check.Scale.REN
    )
    assert checkres is pineko.check.AvailableAtMax.SCVAR
    assert max_as_effective == max_as
    order_list.pop(-1)
    mygrid_new = Fake_grid(order_list)
    checkres, max_as_effective = pineko.check.contains_sv(
        mygrid_new, max_as, max_al, pineko.check.Scale.REN
    )
    assert checkres is pineko.check.AvailableAtMax.BOTH
    assert max_as_effective == max_as - 1
    order_list.append(Order((2, 0, 0, 0, 0)))
    mygrid_noren = Fake_grid(order_list)
    checkres, max_as_effective = pineko.check.contains_sv(
        mygrid_noren, max_as, max_al, pineko.check.Scale.REN
    )
    assert checkres is pineko.check.AvailableAtMax.CENTRAL
    assert max_as_effective == max_as
    checkres, max_as_effective = pineko.check.contains_sv(
        mygrid_noren, max_as - 1, max_al, pineko.check.Scale.REN
    )
    assert checkres is pineko.check.AvailableAtMax.BOTH
    assert max_as_effective == max_as - 1
    order_list.pop(0)
    mygrid_noren = Fake_grid(order_list)
    checkres, max_as_effective = pineko.check.contains_sv(
        mygrid_noren, max_as, max_al, pineko.check.Scale.REN
    )
    assert checkres is pineko.check.AvailableAtMax.CENTRAL
    assert max_as_effective == max_as - 1

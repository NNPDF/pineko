import pineappl

import pineko.check
import pineko.theory


class Fake_grid:
    def __init__(self, order_list, convolutions=[]):
        self.orderlist = order_list
        self.convolutions = convolutions

    def orders(self):
        return [order._raw for order in self.orderlist]


class Order:
    def __init__(self, order_tup):
        self.orders = order_tup
        self._raw = pineappl.boc.Order(*order_tup)

    def as_tuple(self):
        return self.orders


def test_check_scvar_evolve():
    max_as = 3
    max_al = 0

    grid_both = Fake_grid(
        [
            Order((0, 0, 0, 0, 0)),
            Order((1, 0, 0, 0, 0)),
            Order((2, 0, 0, 0, 0)),
            Order((2, 0, 1, 0, 0)),
        ]
    )
    pineko.theory.check_scvar_evolve(
        grid_both,
        max_as,
        max_al,
        pineko.check.Scale.REN,
    )

    grid_central = Fake_grid(
        [
            Order((0, 0, 0, 0, 0)),
            Order((1, 0, 0, 0, 0)),
            Order((2, 0, 0, 0, 0)),
        ]
    )
    pineko.theory.check_scvar_evolve(
        grid_central,
        max_as,
        max_al,
        pineko.check.Scale.REN,
    )

    grid_scvar = Fake_grid(
        [
            Order((0, 0, 0, 0, 0)),
            Order((1, 0, 0, 0, 0)),
            Order((2, 0, 1, 0, 0)),
        ]
    )
    pineko.theory.check_scvar_evolve(
        grid_scvar,
        max_as,
        max_al,
        pineko.check.Scale.REN,
    )

    pineko.theory.check_scvar_evolve(
        grid_scvar,
        1,
        max_al,
        pineko.check.Scale.REN,
    )

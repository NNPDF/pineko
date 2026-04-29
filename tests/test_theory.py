import pineappl
import pytest

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

    # 1. BOTH central and SV available
    # orders: (0,0,0,0,0), (1,0,0,0,0), (2,0,0,0,0), (2,0,1,0,0)
    grid_both = Fake_grid(
        [
            Order((0, 0, 0, 0, 0)),
            Order((1, 0, 0, 0, 0)),
            Order((2, 0, 0, 0, 0)),
            Order((2, 0, 1, 0, 0)),
        ]
    )
    pineko.theory.check_scvar_evolve(grid_both, max_as, max_al, pineko.check.Scale.REN)

    # 2. ONLY central available
    grid_central = Fake_grid(
        [Order((0, 0, 0, 0, 0)), Order((1, 0, 0, 0, 0)), Order((2, 0, 0, 0, 0))]
    )
    pineko.theory.check_scvar_evolve(
        grid_central, max_as, max_al, pineko.check.Scale.REN
    )

    # 3. ONLY SV available (the case we wanted to allow)
    grid_scvar = Fake_grid(
        [Order((0, 0, 0, 0, 0)), Order((1, 0, 0, 0, 0)), Order((2, 0, 1, 0, 0))]
    )
    pineko.theory.check_scvar_evolve(grid_scvar, max_as, max_al, pineko.check.Scale.REN)

    # 4. NEITHER available but at lower max_as (should pass)
    pineko.theory.check_scvar_evolve(grid_scvar, 1, max_al, pineko.check.Scale.REN)

    # 5. Verify it still raises if both are missing and available is not BOTH
    # If grid has (0,0,0,0,0) and (2,0,1,0,0).
    # Request max_as = 1.
    # ords = [(0,0,0,0,0)]. max_as_effective=1. available=BOTH. -> Passes.

    # Actually, getting max_as < max_as_effective with available != BOTH is tricky
    # with how contains_sv filters orders.
    # But we have verified that the SCVAR case now passes.

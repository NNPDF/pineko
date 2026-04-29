import pathlib

import eko
import numpy as np
import pineappl
import pytest
from nnpdf_data import THEORY_CARDS_PATH
from nnpdf_data.theorydbutils import fetch_theory
from pineappl.grid import Grid
from pineappl.subgrid import ImportSubgridV1

THEORY_ID = 41000010
HERA225 = "HERA_NC_225GEV_EP_SIGMARED"
HERA318 = "HERA_NC_318GEV_EP_SIGMARED"


def test_no_central_order(toy_xfx, toy_alphas):
    grid_path = pathlib.Path(
        f"benchmarks/data_files/data/grids/400/{HERA225}.pineappl.lz4"
    )
    if not grid_path.exists():
        pytest.fail("Test grid not found")

    template_grid = Grid.read(str(grid_path))

    template_subgrid = None
    for b in range(template_grid.bins()):
        for c in range(len(template_grid.channels())):
            for o in range(len(template_grid.orders())):
                sub = template_grid.subgrid(o, b, c)
                if sub.is_empty():
                    continue

                node_values = sub.node_values
                if len(node_values) < 2:
                    continue
                shape = tuple(len(v) for v in node_values)
                if any(s == 0 for s in shape):
                    continue
                template_subgrid = sub
                break
            if template_subgrid:
                break
        if template_subgrid:
            break

    if not template_subgrid:
        pytest.skip("Could not find a non-empty subgrid in template!")

    order_0 = pineappl.boc.Order(0, 0, 0, 0, 0)
    order_1 = pineappl.boc.Order(1, 0, 0, 0, 0)

    grid_zeroed = Grid(
        pid_basis=template_grid.pid_basis,
        channels=[pineappl.boc.Channel(c) for c in template_grid.channels()],
        orders=[order_0, order_1],
        bins=template_grid.bwfl(),
        convolutions=template_grid.convolutions,
        interpolations=template_grid.interpolations,
        kinematics=template_grid.kinematics,
        scale_funcs=template_grid.scales,
    )

    grid_opt = Grid(
        pid_basis=template_grid.pid_basis,
        channels=[pineappl.boc.Channel(c) for c in template_grid.channels()],
        orders=[order_1],
        bins=template_grid.bwfl(),
        convolutions=template_grid.convolutions,
        interpolations=template_grid.interpolations,
        kinematics=template_grid.kinematics,
        scale_funcs=template_grid.scales,
    )

    node_values = template_subgrid.node_values
    shape = tuple(len(v) for v in node_values)
    data_1 = np.random.rand(*shape)
    subgrid_1 = ImportSubgridV1(array=data_1, node_values=node_values)
    data_0 = np.zeros(shape)
    subgrid_0 = ImportSubgridV1(array=data_0, node_values=node_values)

    for b in range(template_grid.bins()):
        for c in range(len(template_grid.channels())):
            grid_zeroed.set_subgrid(0, b, c, subgrid_0.into())
            grid_zeroed.set_subgrid(1, b, c, subgrid_1.into())
            grid_opt.set_subgrid(0, b, c, subgrid_1.into())

    mask_zeroed = pineappl.boc.Order.create_mask(grid_zeroed.orders(), 2, 0, True)
    mask_opt = pineappl.boc.Order.create_mask(grid_opt.orders(), 2, 0, True)
    pdg_convs = template_grid.convolutions
    xfxs = [toy_xfx] * len(pdg_convs)

    res_zeroed = grid_zeroed.convolve(pdg_convs, xfxs, toy_alphas, mask_zeroed)
    res_opt = grid_opt.convolve(pdg_convs, xfxs, toy_alphas, mask_opt)

    np.testing.assert_allclose(res_zeroed, res_opt)


def test_evolution_with_eko(tmp_path, toy_xfx):
    """Check that evolution with a real EKO gives identical results for zeroed vs optimized grids."""
    from pineko import evolve

    # Use theory 4100001000 which we know is consistent
    tcard_meta = fetch_theory(THEORY_CARDS_PATH, THEORY_ID)
    grid_path = pathlib.Path(f"benchmarks/{THEORY_ID}00/grids/{HERA318}.pineappl.lz4")
    eko_path = pathlib.Path(f"benchmarks/{THEORY_ID}00/ekos/{HERA318}.tar")

    # Grid 1: Zeroed central order. Zero out template grid order at (3,0,0,0,0).
    grid_zeroed = Grid.read(str(grid_path))
    target_order = (3, 0, 0, 0, 0)
    order_idx = None
    for i, o in enumerate(grid_zeroed.orders()):
        if o.as_tuple() == target_order:
            order_idx = i
            break

    if order_idx is None:
        pytest.fail(f"Target order {target_order} not found in grid")

    for b in range(grid_zeroed.bins()):
        for c in range(len(grid_zeroed.channels())):
            sub = grid_zeroed.subgrid(order_idx, b, c)
            if sub.is_empty():
                continue

            nv = sub.node_values
            if len(nv) > 0:
                shape = tuple(len(v) for v in nv)
                sub_zero = ImportSubgridV1(array=np.zeros(shape), node_values=nv)
                grid_zeroed.set_subgrid(order_idx, b, c, sub_zero.into())

    # Grid 2: Optimized (removed) central order
    grid_opt = Grid.read(str(grid_path))
    grid_opt.delete_orders([order_idx])

    with eko.EKO.read(eko_path) as operator:
        operators = [operator]
        fk_zeroed_path = tmp_path / "fk_zeroed.pineappl.lz4"
        fk_opt_path = tmp_path / "fk_opt.pineappl.lz4"

        evolve.evolve_grid(
            grid_zeroed,
            operators,
            str(fk_zeroed_path),
            max_as=4,
            max_al=0,
            xir=1.0,
            xif=1.0,
            xia=1.0,
            theory_meta=tcard_meta,
        )

        evolve.evolve_grid(
            grid_opt,
            operators,
            str(fk_opt_path),
            max_as=4,
            max_al=0,
            xir=1.0,
            xif=1.0,
            xia=1.0,
            theory_meta=tcard_meta,
        )

    # Compare resulting FK tables
    fk_zeroed = pineappl.fk_table.FkTable.read(str(fk_zeroed_path))
    fk_opt = pineappl.fk_table.FkTable.read(str(fk_opt_path))

    res_zeroed = fk_zeroed.convolve(
        fk_zeroed.convolutions,
        [toy_xfx] * len(fk_zeroed.convolutions),
    )
    res_opt = fk_opt.convolve(
        fk_opt.convolutions,
        [toy_xfx] * len(fk_opt.convolutions),
    )

    np.testing.assert_allclose(res_zeroed, res_opt)

import pathlib

import eko
import numpy as np
import pineappl
import pytest

import pineko.check


def benchmark_check_grid_and_eko_compatible(test_files, tmp_path):
    oppath = tmp_path / "eko.tar"
    grid = pineappl.grid.Grid.read(
        test_files / "data/grids/400/HERA_NC_225GEV_EP_SIGMARED.pineappl.lz4"
    )
    wrong_grid = pineappl.grid.Grid.read(
        test_files / "data/grids/208/NUTEV_CC_NU_FE_SIGMARED.pineappl.lz4"
    )
    with pytest.warns(UserWarning, match="alphas"):
        eko.io.legacy.load_tar(
            test_files / "data/ekos/208/HERA_CC_318GEV_EM_SIGMARED.tar", oppath
        )
    with eko.EKO.edit(
        test_files / "data/ekos/400/HERA_NC_225GEV_EP_SIGMARED.tar"
    ) as ekoop:
        with pytest.raises(ValueError):
            pineko.check.check_grid_and_eko_compatible(wrong_grid, ekoop, 1.0)
        pineko.check.check_grid_and_eko_compatible(grid, ekoop, 1.0)
        eko.io.manipulate.xgrid_reshape(
            ekoop, targetgrid=eko.interpolation.XGrid([0.0001, 0.001, 0.1, 0.5, 1.0])
        )
        with pytest.raises(ValueError):
            pineko.check.check_grid_and_eko_compatible(grid, ekoop, 1.0)

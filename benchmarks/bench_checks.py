import eko
import pineappl
import pytest
from eko.io import manipulate

import pineko.check


def benchmark_check_grid_and_eko_compatible(test_files, tmp_path):
    grid = pineappl.grid.Grid.read(
        test_files / "data/grids/400/HERA_NC_225GEV_EP_SIGMARED.pineappl.lz4"
    )
    wrong_grid = pineappl.grid.Grid.read(
        test_files / "data/grids/208/NUTEV_CC_NU_FE_SIGMARED.pineappl.lz4"
    )
    with eko.EKO.edit(
        test_files / "data/ekos/400/HERA_NC_225GEV_EP_SIGMARED.tar"
    ) as ekoop:
        eko_xgrid = ekoop.xgrid.tolist()
        for (eko_mu2, _), _ in ekoop.items():
            with pytest.raises(ValueError):
                pineko.check.check_grid_and_eko_compatible(
                    wrong_grid, eko_xgrid, eko_mu2, 1.0, 3, 3
                )
            pineko.check.check_grid_and_eko_compatible(
                grid, eko_xgrid, eko_mu2, 1.0, 3, 3
            )

        # test a wrong rotation
        wrong_xgrid = eko.interpolation.XGrid([0.0001, 0.001, 0.1, 0.5, 1.0])
        for (eko_mu2, _), op in ekoop.items():
            # TODO: here we can only check inputgrid as this eko has dimension (14,40,14,50)
            # and ekoop.xgrid has 50
            op = manipulate.xgrid_reshape(op, ekoop.xgrid, 4, inputgrid=wrong_xgrid)
            assert op.operator.shape[-1] == len(wrong_xgrid)
            with pytest.raises(ValueError):
                pineko.check.check_grid_and_eko_compatible(
                    grid, wrong_xgrid.tolist(), eko_mu2, 1.0, 10, 10
                )
            # restore xgrid
            op = manipulate.xgrid_reshape(op, wrong_xgrid, 4, inputgrid=ekoop.xgrid)
            assert op.operator.shape[-1] == len(ekoop.xgrid)

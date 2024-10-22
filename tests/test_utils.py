import pytest

from pineko import utils

try:
    import nnpdf_data
except ImportError:
    nnpdf_data = None

@pytest.mark.skipif(nnpdf_data is None, reason="nnpdf extras are not installed in the pypi package creation workflow")
@pytest.mark.parametrize(
    "dsname", ["HERA_NC_318GEV_EAVG_CHARM-SIGMARED", "ATLAS_DY_7TEV_46FB_CC"]
)
def test_nnpdf_grids(dsname):
    """Checks that the grids can be read out from the NNPDF theory metadata."""
    grids = utils.read_grids_from_nnpdf(dsname)
    # Check that we get _something_
    assert len(grids) > 0
    # And that they look like pineappl grids
    for grid_name in grids:
        grid_name.endswith(".pineappl.lz4")

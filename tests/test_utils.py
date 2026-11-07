import pytest

from pineko import configs, utils

try:
    import nnpdf_data  # noqa: F401

    NNPDF_AVAILABLE = True
except ImportError:
    NNPDF_AVAILABLE = False


def test_nnpdf_enabled():
    """Test _nnpdf_enabled check with various config structures."""
    # When configs is None, returns True by default
    assert utils._nnpdf_enabled(None) is True
    # When configs empty dict, generic options not present, returns False
    assert utils._nnpdf_enabled({}) is False
    # When explicit True
    assert utils._nnpdf_enabled({configs.GENERIC_OPTIONS: {"nnpdf": True}}) is True
    # When explicit False
    assert utils._nnpdf_enabled({configs.GENERIC_OPTIONS: {"nnpdf": False}}) is False


def test_read_grids_from_nnpdf_disabled():
    """Test read_grids_from_nnpdf returns None when nnpdf is disabled in configs."""
    cfg = {configs.GENERIC_OPTIONS: {"nnpdf": False}}
    assert utils.read_grids_from_nnpdf("SOME_DATASET", configs=cfg) is None


def test_load_nnpdf_theory_disabled():
    """Test load_nnpdf_theory returns None when nnpdf is disabled in configs."""
    cfg = {configs.GENERIC_OPTIONS: {"nnpdf": False}}
    assert utils.load_nnpdf_theory(53, configs=cfg) is None


@pytest.mark.skipif(not NNPDF_AVAILABLE, reason="nnpdf_data is not installed")
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

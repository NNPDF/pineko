import numpy as np
import pytest

from pineko import kfactor


class FakeAlpha:
    def __init__(self, const_value):
        self.const_value = const_value

    def alphasQ2(self, q2):
        return self.const_value


class FakeGrid:
    def __init__(self, nbins):
        self.nbins = nbins

    def bins(self):
        return self.nbins


def test_compute_scale_factor():
    const_value = 0.01180
    myfakealpha = FakeAlpha(const_value)
    fake_kfactor = [1.1, 1.2, 1.3]
    bin_index = 1
    np.testing.assert_allclose(
        kfactor.compute_scale_factor(
            [0, 0, 0, 0],
            [1, 0, 0, 0],
            5.0**2,
            fake_kfactor,
            bin_index,
            myfakealpha,
        ),
        (1.0 / const_value) * (fake_kfactor[bin_index] - 1.0),
    )
    np.testing.assert_allclose(
        kfactor.compute_scale_factor(
            [0, 0, 0, 0],
            [2, 0, 0, 0],
            5.0**2,
            fake_kfactor,
            bin_index,
            myfakealpha,
        ),
        (1.0 / (const_value**2)) * (fake_kfactor[bin_index] - 1.0),
    )


def test_filter_kfactors():
    fakegrid = FakeGrid(3)
    # This is the case in which kfactor lenght matches with number of bins
    np.testing.assert_allclose(
        kfactor.filter_kfactor(fakegrid, [1.0, 1.2, 1.3]), [1.0, 1.2, 1.3]
    )
    # This is the case in which kfactor lenght > number of bins and kfactors are all the same
    np.testing.assert_allclose(
        kfactor.filter_kfactor(fakegrid, [1.1, 1.1, 1.1, 1.1, 1.1]),
        [1.1, 1.1, 1.1, 1.1, 1.1],
    )
    # This is the case in which kfactor lenght < number of bins and kfactors are all the same
    np.testing.assert_allclose(
        kfactor.filter_kfactor(fakegrid, [1.1, 1.1]), [1.1, 1.1, 1.1]
    )
    # This is the case in which kfactor lenght < number of bins and kfactors are not all the same
    np.testing.assert_allclose(
        kfactor.filter_kfactor(fakegrid, [1.1, 1.3]), [0.0, 0.0, 0.0]
    )
    with pytest.raises(ValueError):
        # This is the case in which kfactor lenght > number of bins and kfactors are not all the same
        kfactor.filter_kfactor(fakegrid, [1.1, 1.2, 1.1, 1.7, 1.1])

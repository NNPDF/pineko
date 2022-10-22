import pathlib
from contextlib import contextmanager

import pytest

import pineko


@pytest.fixture
def test_configs(test_files):
    config_path = pineko.configs.detect(test_files)
    base_configs = pineko.configs.load(config_path)
    return base_configs


@pytest.fixture
def test_files():
    return pathlib.Path(__file__).parents[0] / "data_files/"


@pytest.fixture
def test_pdf():
    return pathlib.Path(__file__).parents[0] / "fakepdfs/"


@pytest.fixture
def lhapdf_path():
    @contextmanager
    def wrapped(newdir):
        import lhapdf  # pylint: disable=import-error, import-outside-toplevel

        paths = lhapdf.paths()
        lhapdf.pathsPrepend(str(newdir))
        try:
            yield
        finally:
            lhapdf.setPaths(paths)

    return wrapped
import os
import pathlib
import shutil
from contextlib import contextmanager

import pytest

import pineko
import pineko.configs


@pytest.fixture
def test_files():
    return pathlib.Path(__file__).parents[0] / "data_files/"


@pytest.fixture
def test_4100001000():
    return pathlib.Path(__file__).parents[0] / "4100001000/"


@pytest.fixture
def test_empty_proj(test_files):
    path = test_files / "empty_proj/"
    yield path
    # Let's clean
    shutil.rmtree(path / "data")
    shutil.rmtree(path / "logs")


@pytest.fixture
def test_configs(test_files):
    config_path = pineko.configs.detect(test_files)
    base_configs = pineko.configs.load(config_path)
    pineko.configs.configs = pineko.configs.defaults(base_configs)
    return pineko.configs.configs


@pytest.fixture
def test_pdf():
    return pathlib.Path(__file__).parents[0] / "fakepdfs/"


@pytest.fixture
def lhapdf_path():
    @contextmanager
    def wrapped(newdir):
        old_path = os.environ.get("NEOPDF_DATA_PATH")
        os.environ["NEOPDF_DATA_PATH"] = str(newdir)
        try:
            yield
        finally:
            if old_path is None:
                os.environ.pop("NEOPDF_DATA_PATH", None)
            else:
                os.environ["NEOPDF_DATA_PATH"] = old_path

    return wrapped


@pytest.fixture
def cd():
    # thanks https://stackoverflow.com/a/24176022/8653979
    @contextmanager
    def wrapped(newdir):
        prevdir = os.getcwd()
        os.chdir(os.path.expanduser(newdir))
        try:
            yield
        finally:
            os.chdir(prevdir)

    return wrapped


@pytest.fixture
def toy_xfx():
    """Toy PDF callable."""

    def xfx(pid, x, q2):
        return 1.0

    return xfx


@pytest.fixture
def toy_alphas():
    """Toy alpha_s callable."""

    def alphas(q2):
        return 1.0

    return alphas

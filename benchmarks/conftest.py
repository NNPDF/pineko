# -*- coding: utf-8 -*-
from contextlib import contextmanager

import pytest


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

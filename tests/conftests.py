# -*- coding: utf-8 -*-
import os
from contextlib import contextmanager

import pytest


@pytest.fixture
def cd():
    # thanks https://stackoverflow.com/questions/431684/
    # how-do-i-change-the-working-directory-in-python/24176022#24176022
    @contextmanager
    def wrapped(newdir):
        prevdir = os.getcwd()
        os.chdir(os.path.expanduser(newdir))
        try:
            yield
        finally:
            os.chdir(prevdir)

    return wrapped

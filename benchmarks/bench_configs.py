import pytest

import pineko


def benchmark_detect(test_files, tmp_path, cd):
    with cd(tmp_path):
        with pytest.raises(FileNotFoundError):
            pineko.configs.detect()
    conf_file = pineko.configs.detect(test_files)
    assert conf_file is not None


def benchmark_load(test_files):
    conf_file = pineko.configs.load(test_files)
    assert conf_file["paths"]["root"] == test_files
    assert conf_file["paths"]["grids"] == "data/grids/"

import pathlib

import pytest

from pineko import scaffold


def test_set_up_project(tmp_path):
    wrong_fake_configs = {
        "paths": {
            "ymldb": tmp_path / "data/ymldb",
            "logs": {"eko": tmp_path / "logs/eko", "fk": ["something", "wrong"]},
        },
        "root": tmp_path,
    }
    with pytest.raises(TypeError):
        scaffold.set_up_project(wrong_fake_configs)
    fake_configs = {
        "paths": {
            "ymldb": tmp_path / "data/ymldb",
            "logs": {"eko": tmp_path / "logs/eko"},
        },
        "root": tmp_path,
    }
    scaffold.set_up_project(fake_configs)
    assert (tmp_path / "data/ymldb").exists()
    assert (tmp_path / "logs/eko").exists()
    print(tmp_path)

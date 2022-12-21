import pathlib

import pytest

from pineko import configs, scaffold


def construct_wrong_fake_configs(tmp_path):
    wrong_fake_configs = {
        "paths": {
            "ymldb": tmp_path / "data/ymldb",
            "logs": {"eko": tmp_path / "logs/eko", "fk": ["something", "wrong"]},
        },
        "root": tmp_path,
    }
    return wrong_fake_configs


def construct_fake_configs_incomplete(tmp_path):
    fake_configs_incomplete = {
        "paths": {
            "ymldb": tmp_path / "data/ymldb",
            "logs": {"eko": tmp_path / "logs/eko"},
        },
        "root": tmp_path,
    }
    return fake_configs_incomplete


def construct_fake_configs(tmp_path):
    fake_configs = {
        "paths": {
            "ymldb": tmp_path / "data/ymldb",
            "operator_cards": tmp_path / "data/operator_cards",
            "grids": tmp_path / "data/grids",
            "operator_card_template_name": "_template.yaml",
            "theory_cards": tmp_path / "data/theory_cards",
            "fktables": tmp_path / "data/fktables",
            "ekos": tmp_path / "data/ekos",
            "logs": {"eko": tmp_path / "logs/eko"},
        },
        "root": tmp_path,
    }
    return fake_configs


def test_set_up_project(tmp_path):
    wrong_fake_configs = construct_wrong_fake_configs(tmp_path)
    with pytest.raises(TypeError):
        scaffold.set_up_project(wrong_fake_configs)
    fake_configs_incomplete = construct_fake_configs_incomplete(tmp_path)
    scaffold.set_up_project(fake_configs_incomplete)
    assert (tmp_path / "data/ymldb").exists()
    assert (tmp_path / "logs/eko").exists()


def test_check_folder(tmp_path):
    # we may fail because we use a wrong config ...
    fake_configs_incomplete = construct_fake_configs_incomplete(tmp_path)
    scaffold.set_up_project(fake_configs_incomplete)
    success, wrong_confs, _wrong_folders = scaffold.check_folders(
        fake_configs_incomplete
    )
    assert success == False
    assert [
        "operator_cards",
        "grids",
        "operator_card_template_name",
        "theory_cards",
        "fktables",
        "ekos",
    ] == wrong_confs
    # or because we didn't setup up properly ...
    fake_configs = construct_fake_configs(tmp_path)
    success, wrong_confs, wrong_folders = scaffold.check_folders(fake_configs)
    assert success == False
    assert len(wrong_confs) == 0
    for key in wrong_folders:
        if not isinstance(wrong_folders[key], dict):
            assert key in configs.needed_keys
    # but if we use our function we have to be safe.
    scaffold.set_up_project(fake_configs)
    assert scaffold.check_folders(fake_configs)[0] == True

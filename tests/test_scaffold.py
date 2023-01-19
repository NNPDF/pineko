import pathlib

import pytest

from pineko import configs, scaffold


def test_set_up_project(my_tmp_path, wrong_fake_configs, fake_configs_incomplete):
    with pytest.raises(TypeError):
        scaffold.set_up_project(wrong_fake_configs)
    scaffold.set_up_project(fake_configs_incomplete)
    assert (my_tmp_path / "data/ymldb").exists()
    assert (my_tmp_path / "logs/eko").exists()


def test_check_folder(fake_configs_incomplete, fake_configs):
    # we may fail because we use a wrong config ...
    scaffold.set_up_project(fake_configs_incomplete)
    incomplete_check = scaffold.check_folders(fake_configs_incomplete)
    assert incomplete_check.success == False
    assert [
        "operator_cards",
        "grids",
        "operator_card_template_name",
        "theory_cards",
        "fktables",
        "ekos",
    ] == incomplete_check.confs
    # or because we didn't setup up properly ...
    fake_check = scaffold.check_folders(fake_configs)
    assert fake_check.success == False
    assert len(fake_check.confs) == 0
    for key in fake_check.folders:
        if not isinstance(fake_check.folders[key], dict):
            assert key in configs.NEEDED_KEYS
    # but if we use our function we have to be safe.
    scaffold.set_up_project(fake_configs)
    assert scaffold.check_folders(fake_configs).success == True

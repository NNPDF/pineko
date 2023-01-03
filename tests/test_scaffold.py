import pathlib

import pytest

from pineko import configs, scaffold


def test_set_up_project(
    my_tmp_path, construct_wrong_fake_configs, construct_fake_configs_incomplete
):
    with pytest.raises(TypeError):
        scaffold.set_up_project(construct_wrong_fake_configs)
    scaffold.set_up_project(construct_fake_configs_incomplete)
    assert (my_tmp_path / "data/ymldb").exists()
    assert (my_tmp_path / "logs/eko").exists()


def test_check_folder(construct_fake_configs_incomplete, construct_fake_configs):
    # we may fail because we use a wrong config ...
    scaffold.set_up_project(construct_fake_configs_incomplete)
    success, wrong_confs, _wrong_folders = scaffold.check_folders(
        construct_fake_configs_incomplete
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
    success, wrong_confs, wrong_folders = scaffold.check_folders(construct_fake_configs)
    assert success == False
    assert len(wrong_confs) == 0
    for key in wrong_folders:
        if not isinstance(wrong_folders[key], dict):
            assert key in configs.NEEDED_KEYS
    # but if we use our function we have to be safe.
    scaffold.set_up_project(construct_fake_configs)
    assert scaffold.check_folders(construct_fake_configs)[0] == True
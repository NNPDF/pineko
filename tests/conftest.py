import pytest


@pytest.fixture
def my_tmp_path(tmp_path):
    return tmp_path


@pytest.fixture
def construct_wrong_fake_configs(my_tmp_path):
    """This configs are wrong because under logs/fk there is a list and not a string."""
    wrong_fake_configs = {
        "paths": {
            "ymldb": my_tmp_path / "data/ymldb",
            "logs": {"eko": my_tmp_path / "logs/eko", "fk": ["something", "wrong"]},
        },
        "root": my_tmp_path,
    }
    return wrong_fake_configs


@pytest.fixture
def construct_fake_configs_incomplete(my_tmp_path):
    fake_configs_incomplete = {
        "paths": {
            "ymldb": my_tmp_path / "data/ymldb",
            "logs": {"eko": my_tmp_path / "logs/eko"},
        },
        "root": my_tmp_path,
    }
    return fake_configs_incomplete


@pytest.fixture
def construct_fake_configs(my_tmp_path):
    fake_configs = {
        "paths": {
            "ymldb": my_tmp_path / "data/ymldb",
            "operator_cards": my_tmp_path / "data/operator_cards",
            "grids": my_tmp_path / "data/grids",
            "operator_card_template_name": "_template.yaml",
            "theory_cards": my_tmp_path / "data/theory_cards",
            "fktables": my_tmp_path / "data/fktables",
            "ekos": my_tmp_path / "data/ekos",
            "logs": {"eko": my_tmp_path / "logs/eko"},
        },
        "root": my_tmp_path,
    }
    return fake_configs

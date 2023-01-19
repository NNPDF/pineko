import pytest


@pytest.fixture
def wrong_fake_configs(tmp_path):
    """This configs are wrong because under logs/fk there is a list and not a string."""
    wrong_fake_configs = {
        "paths": {
            "ymldb": tmp_path / "data" / "ymldb",
            "logs": {"eko": tmp_path / "logs" / "eko", "fk": ["something", "wrong"]},
        },
        "root": tmp_path,
    }
    return wrong_fake_configs


@pytest.fixture
def fake_configs_incomplete(tmp_path):
    "This configs are incomplete because we are missing for instance the ekos and fktables keys."
    fake_configs_incomplete = {
        "paths": {
            "ymldb": tmp_path / "data" / "ymldb",
            "logs": {"eko": tmp_path / "logs" / "eko"},
        },
        "root": tmp_path,
    }
    return fake_configs_incomplete


@pytest.fixture
def fake_configs(tmp_path):
    fake_configs = {
        "paths": {
            "ymldb": tmp_path / "data" / "ymldb",
            "operator_cards": tmp_path / "data" / "operator_cards",
            "grids": tmp_path / "data" / "grids",
            "operator_card_template_name": "_template.yaml",
            "theory_cards": tmp_path / "data" / "theory_cards",
            "fktables": tmp_path / "data" / "fktables",
            "ekos": tmp_path / "data" / "ekos",
            "logs": {"eko": tmp_path / "logs" / "eko"},
        },
        "root": tmp_path,
    }
    return fake_configs

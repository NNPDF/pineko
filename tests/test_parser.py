import pytest
import yaml

from pineko import parser


def test_load_yaml_operation_normalization(tmp_path):
    """Test that _load_yaml normalizes operation strings and handles None."""
    # Operation in lowercase should be converted to uppercase
    yaml_file1 = tmp_path / "dataset1.yaml"
    data1 = {"operation": "compound", "operands": [["grid1"]]}
    yaml_file1.write_text(yaml.safe_dump(data1), encoding="utf-8")

    res1 = parser._load_yaml(yaml_file1)
    assert res1["operation"] == "COMPOUND"
    assert res1["operands"] == [["grid1"]]

    # None operation should be converted to 'NULL'
    yaml_file2 = tmp_path / "dataset2.yaml"
    data2 = {"operation": None, "operands": [["grid2"]]}
    yaml_file2.write_text(yaml.safe_dump(data2), encoding="utf-8")

    res2 = parser._load_yaml(yaml_file2)
    assert res2["operation"] == "NULL"


def test_load_yaml_file_not_found(tmp_path):
    """Test that _load_yaml raises YamlFileNotFound for non-existent files."""
    missing = tmp_path / "does_not_exist.yaml"
    with pytest.raises(parser.YamlFileNotFound):
        parser._load_yaml(missing)


def test_get_yaml_information_success(tmp_path):
    """Test get_yaml_information returns metadata and resolved grid paths."""
    grids_dir = tmp_path / "grids"
    grids_dir.mkdir()

    # Create dummy grid files
    grid1 = grids_dir / f"grid1.{parser.EXT}"
    grid2 = grids_dir / f"grid2.{parser.EXT}"
    grid3 = grids_dir / f"grid3.{parser.EXT}"
    grid1.touch()
    grid2.touch()
    grid3.touch()

    yaml_file = tmp_path / "dataset.yaml"
    data = {
        "dataset_name": "TEST_DATASET",
        "operation": "ratio",
        "operands": [["grid1", "grid2"], ["grid3"]],
    }
    yaml_file.write_text(yaml.safe_dump(data), encoding="utf-8")

    yaml_content, ret = parser.get_yaml_information(yaml_file, grids_dir)
    assert yaml_content["dataset_name"] == "TEST_DATASET"
    assert yaml_content["operation"] == "RATIO"
    assert ret == [[grid1, grid2], [grid3]]


def test_get_yaml_information_missing_grid(tmp_path):
    """Test get_yaml_information raises GridFileNotFound when an operand grid is missing."""
    grids_dir = tmp_path / "grids"
    grids_dir.mkdir()

    # Create only one grid, omit the second
    grid1 = grids_dir / f"grid1.{parser.EXT}"
    grid1.touch()

    yaml_file = tmp_path / "dataset.yaml"
    data = {
        "operation": "null",
        "operands": [["grid1"], ["missing_grid"]],
    }
    yaml_file.write_text(yaml.safe_dump(data), encoding="utf-8")

    with pytest.raises(parser.GridFileNotFound, match="Failed to find.*missing_grid"):
        parser.get_yaml_information(yaml_file, grids_dir)

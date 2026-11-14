"""Unit tests for TheoryBuilder in pineko.theory."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

import pineko.configs
from pineko.theory import TheoryBuilder


@pytest.fixture
def builder(tmp_path, monkeypatch):
    """Create a default TheoryBuilder instance with configured paths."""
    monkeypatch.setattr(
        pineko.configs,
        "configs",
        {
            "paths": {
                "ekos": tmp_path / "ekos",
                "grids": tmp_path / "grids",
                "operator_cards": tmp_path / "operator_cards",
                "fktables": tmp_path / "fktables",
            }
        },
    )
    return TheoryBuilder(theory_id=100, datasets=["test_dataset"])


def test_inherit_grid_new(builder, tmp_path):
    """Test inherit_grid when target does not exist."""
    grid = tmp_path / "source" / "test.pineappl.lz4"
    mock_new = MagicMock(spec=Path)
    mock_new.is_symlink.return_value = False
    mock_new.exists.return_value = False

    other = MagicMock()
    other.__truediv__.return_value = mock_new

    builder.inherit_grid("test", grid, other)

    mock_new.unlink.assert_not_called()
    mock_new.symlink_to.assert_called_once_with(grid)


def test_inherit_grid_existing_no_overwrite(builder, tmp_path):
    """Test inherit_grid skips existing grid when overwrite=False."""
    grid = tmp_path / "source" / "test.pineappl.lz4"
    builder.overwrite = False

    mock_new = MagicMock(spec=Path)
    mock_new.is_symlink.return_value = False
    mock_new.exists.return_value = True

    other = MagicMock()
    other.__truediv__.return_value = mock_new

    builder.inherit_grid("test", grid, other)

    mock_new.unlink.assert_not_called()
    mock_new.symlink_to.assert_not_called()


def test_inherit_grid_existing_overwrite(builder, tmp_path):
    """Test inherit_grid unlinks and relinks when overwrite=True."""
    grid = tmp_path / "source" / "test.pineappl.lz4"
    builder.overwrite = True

    mock_new = MagicMock(spec=Path)
    mock_new.is_symlink.return_value = False
    mock_new.exists.return_value = True

    other = MagicMock()
    other.__truediv__.return_value = mock_new

    builder.inherit_grid("test", grid, other)

    mock_new.unlink.assert_called_once()
    mock_new.symlink_to.assert_called_once_with(grid)


def test_inherit_grid_stale_symlink(builder, tmp_path):
    """Test inherit_grid unlinks stale symlink even when overwrite=False."""
    grid = tmp_path / "source" / "test.pineappl.lz4"
    builder.overwrite = False

    mock_new = MagicMock(spec=Path)
    # Stale symlink: is_symlink is True, exists is False
    mock_new.is_symlink.return_value = True
    mock_new.exists.return_value = False

    other = MagicMock()
    other.__truediv__.return_value = mock_new

    builder.inherit_grid("test", grid, other)

    mock_new.unlink.assert_called_once()
    mock_new.symlink_to.assert_called_once_with(grid)


def test_inherit_eko_new(builder, tmp_path):
    """Test inherit_eko when target does not exist."""
    grid = tmp_path / "source" / "test.pineappl.lz4"

    mock_new = MagicMock(spec=Path)
    mock_new.is_symlink.return_value = False
    mock_new.exists.return_value = False

    other = MagicMock()
    other.__truediv__.return_value = mock_new

    with patch("pineko.theory.get_eko_names", return_value=["test"]):
        builder.inherit_eko("test", grid, other)

    mock_new.unlink.assert_not_called()
    mock_new.symlink_to.assert_called_once()


def test_inherit_eko_existing_no_overwrite(builder, tmp_path):
    """Test inherit_eko skips existing eko when overwrite=False."""
    grid = tmp_path / "source" / "test.pineappl.lz4"
    builder.overwrite = False

    mock_new = MagicMock(spec=Path)
    mock_new.is_symlink.return_value = False
    mock_new.exists.return_value = True

    other = MagicMock()
    other.__truediv__.return_value = mock_new

    with patch("pineko.theory.get_eko_names", return_value=["test"]):
        builder.inherit_eko("test", grid, other)

    mock_new.unlink.assert_not_called()
    mock_new.symlink_to.assert_not_called()


def test_inherit_eko_existing_overwrite(builder, tmp_path):
    """Test inherit_eko unlinks existing eko when overwrite=True."""
    grid = tmp_path / "source" / "test.pineappl.lz4"
    builder.overwrite = True

    mock_new = MagicMock(spec=Path)
    mock_new.is_symlink.return_value = False
    mock_new.exists.return_value = True

    other = MagicMock()
    other.__truediv__.return_value = mock_new

    with patch("pineko.theory.get_eko_names", return_value=["test"]):
        builder.inherit_eko("test", grid, other)

    mock_new.unlink.assert_called_once()
    mock_new.symlink_to.assert_called_once()


def test_inherit_eko_stale_symlink(builder, tmp_path):
    """Test inherit_eko unlinks stale symlink even when overwrite=False."""
    grid = tmp_path / "source" / "test.pineappl.lz4"
    builder.overwrite = False

    mock_new = MagicMock(spec=Path)
    # Stale symlink: is_symlink is True, exists is False
    mock_new.is_symlink.return_value = True
    mock_new.exists.return_value = False

    other = MagicMock()
    other.__truediv__.return_value = mock_new

    with patch("pineko.theory.get_eko_names", return_value=["test"]):
        builder.inherit_eko("test", grid, other)

    mock_new.unlink.assert_called_once()
    mock_new.symlink_to.assert_called_once()


def test_inherit_eko_multiple_names_continue(builder, tmp_path):
    """Test inherit_eko continues when first eko already exists."""
    grid = tmp_path / "source" / "test.pineappl.lz4"
    builder.overwrite = False

    mock_new1 = MagicMock(spec=Path)
    mock_new1.is_symlink.return_value = False
    mock_new1.exists.return_value = True

    mock_new2 = MagicMock(spec=Path)
    mock_new2.is_symlink.return_value = False
    mock_new2.exists.return_value = False

    def truediv_side_effect(sub):
        if str(sub) == "eko1.tar":
            return mock_new1
        if str(sub) == "eko2.tar":
            return mock_new2
        return MagicMock()

    other = MagicMock()
    other.__truediv__.side_effect = truediv_side_effect

    with patch("pineko.theory.get_eko_names", return_value=["eko1", "eko2"]):
        builder.inherit_eko("test", grid, other)

    # eko1 was skipped (no unlink, no symlink_to)
    mock_new1.unlink.assert_not_called()
    mock_new1.symlink_to.assert_not_called()

    # eko2 was processed (symlink_to called)
    mock_new2.unlink.assert_not_called()
    mock_new2.symlink_to.assert_called_once()

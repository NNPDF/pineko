"""Tests for pineko convolve CLI."""

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from pineko.cli._base import command


def test_convolve_cli_reads_operators_without_edit(tmp_path):
    """Test that pineko convolve opens operators in read-only mode.

    Verifies that multiple operators are supported without calling EKO.edit.
    """
    grid_path = tmp_path / "grid.pineappl.lz4"
    grid_path.write_text("dummy")
    op1 = tmp_path / "op1.tar"
    op1.write_text("dummy1")
    op2 = tmp_path / "op2.tar"
    op2.write_text("dummy2")
    fk_path = tmp_path / "fk.pineappl.lz4"

    runner = CliRunner()
    with patch("pineappl.grid.Grid.read"), patch(
        "pineko.theory_card.load", return_value={"ID": 400}
    ), patch("eko.EKO.read") as mock_eko_read, patch(
        "eko.EKO.edit"
    ) as mock_eko_edit, patch(
        "pineko.evolve.evolve_grid", return_value=(MagicMock(), MagicMock(), None)
    ) as mock_evolve:
        mock_op1 = MagicMock()
        mock_op2 = MagicMock()
        mock_eko_read.side_effect = [mock_op1, mock_op2]

        result = runner.invoke(
            command,
            [
                "convolve",
                str(fk_path),
                str(grid_path),
                "400",
                "1",
                "0",
                str(op1),
                str(op2),
            ],
        )

        assert result.exit_code == 0
        assert mock_eko_read.call_count == 2
        mock_eko_edit.assert_not_called()
        mock_evolve.assert_called_once()
        operators_arg = mock_evolve.call_args[0][1]
        assert len(operators_arg) == 2


def test_convolve_cli_requires_operators(tmp_path):
    """Test that convolve reports error when no operators are given."""
    grid_path = tmp_path / "grid.pineappl.lz4"
    grid_path.write_text("dummy")
    fk_path = tmp_path / "fk.pineappl.lz4"

    runner = CliRunner()
    result = runner.invoke(
        command,
        ["convolve", str(fk_path), str(grid_path), "400", "1", "0"],
    )

    assert result.exit_code != 0
    assert "Missing argument" in result.output

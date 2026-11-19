"""Unit tests for TheoryBuilder in pineko.theory."""

from pathlib import Path
from unittest.mock import patch

import pytest

import pineko.configs
from pineko.theory import TheoryBuilder


class FakeSymlinkPath:
    """Simulates a filesystem path raising FileExistsError on symlink_to if not unlinked first.

    This directly tests the symptom of the bug (#264) without depending on host OS privileges.
    """

    def __init__(self, name: str, is_symlink: bool = False, exists: bool = False):
        self.name = name
        self._is_symlink = is_symlink
        self._exists = exists
        self.target = None
        self.unlinked = False

    def is_symlink(self) -> bool:
        return self._is_symlink

    def exists(self) -> bool:
        return self._exists

    def unlink(self) -> None:
        self.unlinked = True
        self._is_symlink = False
        self._exists = False

    def symlink_to(self, target) -> None:
        if self._is_symlink or self._exists:
            raise FileExistsError(f"[Errno 17] File exists: '{self.name}'")
        self._is_symlink = True
        self._exists = True
        self.target = target

    def __repr__(self):
        return (
            f"FakeSymlinkPath({self.name!r}, is_symlink={self._is_symlink}, "
            f"exists={self._exists})"
        )


class FakeDirectory:
    """Simulates a directory whose `/` operator returns configured FakeSymlinkPath objects."""

    def __init__(self, files: dict[str, FakeSymlinkPath] | None = None):
        self.files = files or {}

    def __truediv__(self, name):
        return self.files.get(str(name), FakeSymlinkPath(str(name)))


def _can_create_symlink(tmp_path: Path) -> bool:
    """Check if the current runtime environment supports creating symlinks."""
    src = tmp_path / "_symlink_probe_src"
    src.write_text("probe")
    link = tmp_path / "_symlink_probe_link"
    try:
        link.symlink_to(src)
        return True
    except OSError:
        return False
    finally:
        if link.is_symlink() or link.exists():
            link.unlink()
        if src.exists():
            src.unlink()


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
                "logs": {"eko": tmp_path / "logs" / "eko"},
            }
        },
    )
    return TheoryBuilder(theory_id=100, datasets=["test_dataset"])


# ---------------------------------------------------------------------------
# prepare_path tests
# ---------------------------------------------------------------------------


def test_prepare_path_nonexistent(builder, tmp_path):
    """Test prepare_path returns True when destination file does not exist."""
    path = tmp_path / "new_file.txt"
    assert builder.prepare_path(path, "test") is True


def test_prepare_path_existing_no_overwrite(builder, tmp_path):
    """Test prepare_path returns False and preserves file when overwrite=False."""
    path = tmp_path / "existing.txt"
    path.write_text("existing data")
    builder.overwrite = False

    assert builder.prepare_path(path, "test") is False
    assert path.exists()
    assert path.read_text() == "existing data"


def test_prepare_path_existing_overwrite(builder, tmp_path):
    """Test prepare_path unlinks existing file and returns True when overwrite=True."""
    path = tmp_path / "existing.txt"
    path.write_text("existing data")
    builder.overwrite = True

    assert builder.prepare_path(path, "test") is True
    assert not path.exists()


def test_prepare_path_stale_symlink(builder):
    """Test prepare_path detects stale symlink, unlinks it, and prevents FileExistsError."""
    fake = FakeSymlinkPath("stale.txt", is_symlink=True, exists=False)
    builder.overwrite = False

    # Calling symlink_to without prepare_path raises FileExistsError
    with pytest.raises(FileExistsError):
        FakeSymlinkPath("stale.txt", is_symlink=True, exists=False).symlink_to("target")

    # prepare_path clears the stale symlink
    assert builder.prepare_path(fake, "test") is True
    assert fake.unlinked is True
    # Now symlink_to succeeds
    fake.symlink_to("target")
    assert fake.target == "target"


# ---------------------------------------------------------------------------
# inherit_grid tests
# ---------------------------------------------------------------------------


def test_inherit_grid_new(builder, tmp_path):
    """Test inherit_grid creates new link when destination does not exist."""
    grid = tmp_path / "source" / "test.pineappl.lz4"
    dest = FakeSymlinkPath("test.pineappl.lz4", is_symlink=False, exists=False)
    other = FakeDirectory({"test.pineappl.lz4": dest})

    builder.inherit_grid("test", grid, other)

    assert dest.target == grid


def test_inherit_grid_existing_no_overwrite(builder, tmp_path):
    """Test inherit_grid skips existing grid when overwrite=False."""
    grid = tmp_path / "source" / "test.pineappl.lz4"
    dest = FakeSymlinkPath("test.pineappl.lz4", is_symlink=False, exists=True)
    other = FakeDirectory({"test.pineappl.lz4": dest})
    builder.overwrite = False

    builder.inherit_grid("test", grid, other)

    assert dest.target is None
    assert dest.unlinked is False


def test_inherit_grid_existing_overwrite(builder, tmp_path):
    """Test inherit_grid replaces existing grid when overwrite=True."""
    grid = tmp_path / "source" / "test.pineappl.lz4"
    dest = FakeSymlinkPath("test.pineappl.lz4", is_symlink=False, exists=True)
    other = FakeDirectory({"test.pineappl.lz4": dest})
    builder.overwrite = True

    builder.inherit_grid("test", grid, other)

    assert dest.unlinked is True
    assert dest.target == grid


def test_inherit_grid_stale_symlink(builder, tmp_path):
    """Test inherit_grid removes stale symlink and creates link without FileExistsError."""
    grid = tmp_path / "source" / "test.pineappl.lz4"
    dest = FakeSymlinkPath("test.pineappl.lz4", is_symlink=True, exists=False)
    other = FakeDirectory({"test.pineappl.lz4": dest})
    builder.overwrite = False

    builder.inherit_grid("test", grid, other)

    assert dest.unlinked is True
    assert dest.target == grid


def test_inherit_grid_real_filesystem_stale_symlink(builder, tmp_path):
    """End-to-end test on real filesystem: stale symlink is replaced without FileExistsError."""
    if not _can_create_symlink(tmp_path):
        pytest.skip("Symlink creation not supported in this environment")

    source_grid = tmp_path / "source" / "test.pineappl.lz4"
    source_grid.parent.mkdir(parents=True, exist_ok=True)
    source_grid.write_text("grid data")

    dest_dir = tmp_path / "dest"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_link = dest_dir / "test.pineappl.lz4"

    # Create stale symlink pointing to deleted file
    dead_target = tmp_path / "dead.txt"
    dead_target.write_text("dead")
    dest_link.symlink_to(dead_target)
    dead_target.unlink()

    assert dest_link.is_symlink()
    assert not dest_link.exists()

    builder.overwrite = False
    builder.inherit_grid("test", source_grid, dest_dir)

    assert dest_link.is_symlink()
    assert dest_link.exists()
    assert dest_link.resolve() == source_grid.resolve()


# ---------------------------------------------------------------------------
# inherit_eko tests
# ---------------------------------------------------------------------------


def test_inherit_eko_new(builder, tmp_path):
    """Test inherit_eko creates new link when destination does not exist."""
    grid = tmp_path / "source" / "test.pineappl.lz4"
    dest = FakeSymlinkPath("test.tar", is_symlink=False, exists=False)
    other = FakeDirectory({"test.tar": dest})

    with patch("pineko.theory.get_eko_names", return_value=["test"]):
        builder.inherit_eko("test", grid, other)

    assert dest.target == builder.ekos_path() / "test.tar"


def test_inherit_eko_existing_no_overwrite(builder, tmp_path):
    """Test inherit_eko skips existing eko when overwrite=False."""
    grid = tmp_path / "source" / "test.pineappl.lz4"
    dest = FakeSymlinkPath("test.tar", is_symlink=False, exists=True)
    other = FakeDirectory({"test.tar": dest})
    builder.overwrite = False

    with patch("pineko.theory.get_eko_names", return_value=["test"]):
        builder.inherit_eko("test", grid, other)

    assert dest.target is None
    assert dest.unlinked is False


def test_inherit_eko_existing_overwrite(builder, tmp_path):
    """Test inherit_eko replaces existing eko when overwrite=True."""
    grid = tmp_path / "source" / "test.pineappl.lz4"
    dest = FakeSymlinkPath("test.tar", is_symlink=False, exists=True)
    other = FakeDirectory({"test.tar": dest})
    builder.overwrite = True

    with patch("pineko.theory.get_eko_names", return_value=["test"]):
        builder.inherit_eko("test", grid, other)

    assert dest.unlinked is True
    assert dest.target == builder.ekos_path() / "test.tar"


def test_inherit_eko_stale_symlink(builder, tmp_path):
    """Test inherit_eko removes stale symlink and links without FileExistsError."""
    grid = tmp_path / "source" / "test.pineappl.lz4"
    dest = FakeSymlinkPath("test.tar", is_symlink=True, exists=False)
    other = FakeDirectory({"test.tar": dest})
    builder.overwrite = False

    with patch("pineko.theory.get_eko_names", return_value=["test"]):
        builder.inherit_eko("test", grid, other)

    assert dest.unlinked is True
    assert dest.target == builder.ekos_path() / "test.tar"


def test_inherit_eko_multiple_names_continue(builder, tmp_path):
    """Test inherit_eko continues to subsequent ekos when the first already exists."""
    grid = tmp_path / "source" / "test.pineappl.lz4"
    builder.overwrite = False

    dest1 = FakeSymlinkPath("eko1.tar", is_symlink=False, exists=True)
    dest2 = FakeSymlinkPath("eko2.tar", is_symlink=False, exists=False)

    other = FakeDirectory({"eko1.tar": dest1, "eko2.tar": dest2})

    with patch("pineko.theory.get_eko_names", return_value=["eko1", "eko2"]):
        builder.inherit_eko("test", grid, other)

    # eko1 was skipped
    assert dest1.target is None
    assert dest1.unlinked is False
    # eko2 was processed
    assert dest2.target == builder.ekos_path() / "eko2.tar"


def test_inherit_eko_real_filesystem_stale_symlink(builder, tmp_path):
    """End-to-end test on real filesystem: inherit_eko replaces stale symlink."""
    if not _can_create_symlink(tmp_path):
        pytest.skip("Symlink creation not supported in this environment")

    eko_dir = builder.ekos_path()
    eko_dir.mkdir(parents=True, exist_ok=True)
    source_eko = eko_dir / "test.tar"
    source_eko.write_text("eko data")

    dest_dir = tmp_path / "dest_ekos"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_link = dest_dir / "test.tar"

    # Create stale symlink
    dead_target = tmp_path / "dead_eko.txt"
    dead_target.write_text("dead")
    dest_link.symlink_to(dead_target)
    dead_target.unlink()

    assert dest_link.is_symlink()
    assert not dest_link.exists()

    grid = tmp_path / "dummy.pineappl.lz4"
    with patch("pineko.theory.get_eko_names", return_value=["test"]):
        builder.inherit_eko("test", grid, dest_dir)

    assert dest_link.is_symlink()
    assert dest_link.exists()
    assert dest_link.resolve() == source_eko.resolve()


# ---------------------------------------------------------------------------
# eko loop continuation tests
# ---------------------------------------------------------------------------


def test_eko_multiple_names_continue(builder, tmp_path):
    """Test eko() continues computing remaining ekos when an earlier eko already exists."""
    builder.overwrite = False
    builder.ekos_path().mkdir(parents=True, exist_ok=True)

    # eko1.tar already exists
    existing_eko = builder.ekos_path() / "eko1.tar"
    existing_eko.write_text("already computed")

    # eko2.tar does not exist
    new_eko = builder.ekos_path() / "eko2.tar"

    grid = tmp_path / "test.pineappl.lz4"
    tcard = {"PTOEKO": 1, "Qref": 1.65, "MaxNfPdf": 5}

    with (
        patch("pineko.theory.get_eko_names", return_value=["eko1", "eko2"]),
        patch.object(builder, "activate_logging"),
        patch.object(builder, "load_operator_card", return_value={}),
        patch("eko.io.runcards.Legacy"),
        patch("eko.io.runcards.OperatorCard.from_dict"),
        patch("pineko.theory.solve") as mock_solve,
    ):
        builder.eko("test", grid, tcard, int_cores=1)

    # solve should be called exactly once: for eko2 (eko1 was skipped with continue)
    assert mock_solve.call_count == 1
    assert mock_solve.call_args[0][2] == new_eko

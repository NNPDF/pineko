"""
    Suite of tests that go through the entire process of creating a new fktable
    from a empty folder.

    The target theory is 400 and the relevant `.toml`, theory runcard and eko template
    are downloaded from https://github.com/NNPDF/theories during this test so this tests
    has the double effect of ensuring compatibility between both repositories.
"""
from pathlib import Path
from subprocess import run
from urllib.request import urlretrieve

import numpy as np
from pineappl.fk_table import FkTable
from yaml import safe_load

THEORIES_REPO = "https://raw.githubusercontent.com/NNPDF/theories/main"
THEORYID = 400


def _download_resources(filename, tmp_path):
    """Download resources (filename) from the theories repo and put it in the same path
    relative to THEORIES_REPO
    """
    output_file = tmp_path / filename
    output_file.parent.mkdir(exist_ok=True)
    urlretrieve(f"{THEORIES_REPO}/{filename}", output_file)


def _download_dataset(dataset, theoryid, tmp_path):
    """Download both the yaml file and all grids for a given dataset for a given theory"""
    yaml_file = f"data/yamldb/{theoryid}/{dataset}.yaml"
    _download_resources(yaml_file, tmp_path)
    # However, the yaml file goes into the "root" of the yaml directory, move it there!
    right_yaml = tmp_path / "data" / "yamldb" / f"{dataset}.yaml"
    (tmp_path / yaml_file).rename(right_yaml)
    # Download the relevant grids for this dataset
    res = safe_load(right_yaml.open("r", encoding="utf-8"))
    grids = [i for j in res["operands"] for i in j]
    for grid_name in grids:
        _download_resources(f"data/grids/400/{grid_name}.pineappl.lz4", tmp_path)
    return grids


class _FakePDF:
    """A Fake lhapdf-like PDF to evolve the grids"""

    def __init__(self):
        pids = np.arange(-6, 7, dtype=int)
        pids[6] = 21

        alphas = np.linspace(0.2, 0.8, len(pids))
        betas = np.linspace(1.2, 3.8, len(pids))

        self._alphas = dict(zip(pids, alphas))
        self._betas = dict(zip(pids, betas))

    def xfxQ2(self, pid, x, q2):
        """Compute x^alpha*(1-x)^alpha"""
        alpha = self._alphas[pid]
        beta = self._betas[pid]
        return np.power(x, alpha) * np.power(1 - x, beta)


def test_regression(tmp_path, rebuild=False):
    """Run pineko through subprocess to ensure that the shell scripts are working exactly
    as intended.
    """
    # We start by downloading pineko.toml in order to generate the folder structure
    _download_resources("pineko.toml", tmp_path)
    # Which we create... now!
    run(["pineko", "scaffold", "new"], cwd=tmp_path, check=True)

    # Now download other necessary objects
    _download_resources(f"data/theory_cards/{THEORYID}.yaml", tmp_path)
    _download_resources(f"data/operator_cards/{THEORYID}/_template.yaml", tmp_path)

    # And use some small (but not trivial!) dataset to test
    dataset = "LHCBWZMU8TEV"
    gridnames = _download_dataset(dataset, THEORYID, tmp_path)

    # Now go, first with eko creation
    run(
        ["pineko", "theory", "opcards", str(THEORYID), dataset],
        cwd=tmp_path,
        check=True,
    )
    run(["pineko", "theory", "ekos", str(THEORYID), dataset], cwd=tmp_path, check=True)

    # Then FK Table production!
    run(["pineko", "theory", "fks", str(THEORYID), dataset], cwd=tmp_path, check=True)

    # Now loop over the grids and check the results of the convolution with the PDF
    pdf = _FakePDF()
    regression_path = Path("regression_data") / f"{dataset}.npy"

    result = []
    for grid_name in gridnames:
        fkt = FkTable.read(
            tmp_path / "data" / "fktables" / str(THEORYID) / f"{grid_name}.pineappl.lz4"
        )
        result.append(fkt.convolute_with_one(2212, pdf.xfxQ2))
    result = np.concatenate(result)

    if rebuild:
        np.save(regression_path, result)

    regression_data = np.load(regression_path)
    np.allclose(regression_data, result)

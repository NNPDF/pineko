<p align="center">
  <a href="https://pineko.readthedocs.io/"><img alt="PINEKO" src="https://raw.githubusercontent.com/N3PDF/pineko/main/docs/source/img/Logo.png" width=200></a>
</p>

<p align="center">
  <a href="https://github.com/N3PDF/pineko/actions/workflows/unittests.yml"><img alt="Tests" src="https://github.com/N3PDF/pineko/actions/workflows/unittests.yml/badge.svg" /></a>
  <a href="https://pineko.readthedocs.io/en/latest/?badge=latest"><img alt="Docs" src="https://readthedocs.org/projects/pineko/badge/?version=latest"></a>
  <a href="https://codecov.io/gh/NNPDF/pineko"><img src="https://codecov.io/gh/NNPDF/pineko/branch/main/graph/badge.svg" /></a>
  <a href="https://www.codefactor.io/repository/github/nnpdf/pineko"><img src="https://www.codefactor.io/repository/github/nnpdf/pineko/badge" alt="CodeFactor" /></a>
</p>

PINEKO is a Python module to produce fktables from interpolation grids and EKOs.

## Installation
PINEKO is available via
- PyPI: <a href="https://pypi.org/project/pineko/"><img alt="PyPI" src="https://img.shields.io/pypi/v/pineko"/></a>
```bash
pip install pineko
```

### Development

If you want to install from source you can run
```bash
git clone git@github.com:N3PDF/pineko.git
cd pineko
poetry install
```

To setup `poetry`, and other tools, see [Contribution
Guidelines](https://github.com/N3PDF/pineko/blob/main/.github/CONTRIBUTING.md).

## Documentation
- The documentation is available here: <a href="https://pineko.readthedocs.io/en/latest/"><img alt="Docs" src="https://readthedocs.org/projects/pineko/badge/?version=latest"></a>
- To build the documentation from source run
```bash
cd docs
poetry run make html
```

## Tests and benchmarks
- To run unit test you can do
```bash
poetry run pytest
```

## Contributing
- Your feedback is welcome! If you want to report a (possible) bug or want to ask for a new feature, please raise an issue: <a href="https://github.com/N3PDF/pineko/issues"><img alt="GitHub issues" src="https://img.shields.io/github/issues/N3PDF/pineko"/></a>
- Please follow our [Code of Conduct](https://github.com/N3PDF/pineko/blob/main/.github/CODE_OF_CONDUCT.md) and read the
  [Contribution Guidelines](https://github.com/N3PDF/pineko/blob/main/.github/CONTRIBUTING.md)

# -*- coding: utf-8 -*-
import pathlib

import packutil as pack
from setuptools import setup, find_packages

# write version on the fly - inspired by numpy
MAJOR = 0
MINOR = 0
MICRO = 1

repo_path = pathlib.Path(__file__).absolute().parent


def setup_package():
    # write version
    pack.versions.write_version_py(
        MAJOR,
        MINOR,
        MICRO,
        pack.versions.is_released(repo_path),
        filename="src/pineko/version.py",
    )
    # paste Readme
    with open("README.md", "r") as fh:
        long_description = fh.read()
    # do it
    setup(
        name="pineko",
        version=pack.versions.mkversion(MAJOR, MINOR, MICRO),
        description="Combine PineAPPLgrids and EKOs",
        long_description=long_description,
        long_description_content_type="text/markdown",
        author="A. Candido, S. Carrazza, J. Cruz Martinez, F. Hekhorn, C. Schwan",
        author_email="stefano.carrazza@cern.ch",
        url="https://github.com/N3PDF/pineko",
        package_dir={"": "src"},
        packages=find_packages("src"),
        classifiers=[
            "Operating System :: Unix",
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Topic :: Scientific/Engineering",
            "Topic :: Scientific/Engineering :: Physics",
        ],
        install_requires=[
            "eko<0.7",
            "pineappl",
            "pyyaml",
            "numpy",
        ],
        python_requires=">=3.7",
    )


if __name__ == "__main__":
    setup_package()

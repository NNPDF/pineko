# -*- coding: utf-8 -*-
# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

import inspect
import pathlib

import pineko

here = pathlib.Path(__file__).absolute().parent

# -- Project information -----------------------------------------------------

project = "pineko"
copyright = "2022, Andrea Barontini, Alessandro Candido, Felix Hekhorn"
author = "Andrea Barontini, Alessandro Candido, Felix Hekhorn"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.doctest",
    "sphinx.ext.intersphinx",
    "sphinx.ext.todo",
    "sphinx.ext.coverage",
    "sphinx.ext.mathjax",
    "sphinx.ext.ifconfig",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosectionlabel",
    "sphinxcontrib.bibtex",
    "sphinx.ext.napoleon",
    "sphinx.ext.graphviz",
    "sphinx.ext.extlinks",
]
autosectionlabel_prefix_document = True
# autosectionlabel_maxdepth = 10
# Allow to embed rst syntax in  markdown files.
enable_eval_rst = True
# The master toctree document.
master_doc = "index"
bibtex_bibfiles = ["refs.bib"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
#
source_suffix = {
    ".rst": "restructuredtext",
    ".txt": "restructuredtext",
}
use_index=True
# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ["shared/*"]

# A string to be included at the beginning of all files
shared = here / "shared"
rst_prolog = "\n".join(
    [x.read_text(encoding="utf-8") for x in pathlib.Path(shared).glob("*.rst")]
)

extlinks = {
    "yadism": ("https://n3pdf.github.io/yadism/%s", "yadism"),
    "banana": ("https://n3pdf.github.io/banana/%s", "banana"),
    "pineappl": ("https://n3pdf.github.io/pineappl/%s", "pineappl"),
    "eko": ("https://github.com/N3PDF/eko/%s", "eko"),
}
# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".

html_static_path = []

html_css_files = [
    'site.css',
]

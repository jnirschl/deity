"""Sphinx configuration."""
project = "DeITy"
author = "Jeff Nirschl"
copyright = "2022, Jeff Nirschl"
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_click",
    "myst_parser",
]
autodoc_typehints = "description"
html_theme = "furo"

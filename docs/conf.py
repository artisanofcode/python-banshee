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

# pylint: disable=invalid-name,redefined-builtin

# -- Project information -----------------------------------------------------

project = "Banshee"
copyright = "2022, Daniel Knell"
author = "Daniel Knell"
author_url = "https://danielknell.co.uk"


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    "autodocsumm",
    "myst_parser",
    "sphinx_artisan_theme",
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinxcontrib.spelling",
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "artisan"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ["_static"]


myst_enable_extensions = [
    "deflist",
    "dollarmath",
    "fieldlist",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",
]
# autodoc_class_signature = "separated"
autodoc_typehints = "description"
autodoc_typehints_format = "short"

python_use_unqualified_type_names = True
add_module_names = True
modindex_common_prefix = [
    "banshee.",
]

suppress_warnings = [
    "myst.strikethrough",
]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3.8", None),
    "injector": ("https://injector.readthedocs.io/en/latest", None),
}

spelling_lang = "en_GB"
tokenizer_lang = "en_GB"
spelling_word_list_filename = ["../.dictionary"]
spelling_show_suggestions = True
spelling_warning = True

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
import os
import sys

sys.path.insert(
    0,
    os.path.abspath(
        os.path.join(
            os.pardir,
            "conflowgen"
        )
    )
)


# -- Project information -----------------------------------------------------

project = 'ConFlowGen'
project_copyright = '2021, Marvin Kastner and Ole Grasse'
author = 'Marvin Kastner and Ole Grasse'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.todo',
    'sphinx.ext.napoleon',
    'sphinx.ext.mathjax',
    'sphinx.ext.coverage',

    'sphinx_math_dollar',
    'enum_tools.autoenum',
    'sphinx_autodoc_typehints',
    'sphinx_toolbox.more_autodoc.autonamedtuple'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_logo = "../logos/conflowgen_logo_small.png"

html_favicon = "../logos/conflowgen_logo_favicon.png"

add_module_names = False

todo_include_todos = True

autoclass_content = 'both'

mathjax3_config = {
    'tex2jax': {
        'inlineMath': [["\\(", "\\)"]],
        'displayMath': [["\\[", "\\]"]],
    },
}

nitpicky = True
nitpick_ignore = []

with open('.nitpick-exceptions', encoding="utf-8") as f:
    for line in f:
        if line.strip() == "" or line.startswith("#"):
            continue
        sphinx_label, sphinx_object_name = line.split(None, 1)
        sphinx_object_name = sphinx_object_name.strip()
        nitpick_ignore.append((sphinx_label, sphinx_object_name))

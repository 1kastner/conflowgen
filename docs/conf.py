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
import datetime
import os
import sys

# import matplotlib here to avoid that the cache is built while the Jupyter Notebooks that are part of this
# documentation are executed. Because whenever matplotlib is imported in a Jupyter Notebook for the first time,
# it leaves the message "Matplotlib is building the font cache; this may take a moment." which is not looking nice.
from matplotlib.font_manager import fontManager
fontManager.get_default_size()  # just some random action so that the import is not flagged as unnecessary

# include conflowgen from source code, avoid being served an outdated installation
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
author = 'Marvin Kastner and Ole Grasse'
current_year = datetime.datetime.now().year
project_copyright = f'{current_year}, {author}'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    # sphinx-internal extensions
    'sphinx.ext.autodoc',  # automatically document classes
    'sphinx.ext.todo',  # create to-do boxes
    'sphinx.ext.napoleon',  # use google-style document strings
    'sphinx.ext.mathjax',  # support LaTeX-style formula
    'sphinx.ext.intersphinx',  # add links to other docs
    'sphinx.ext.autosectionlabel',  # create reference for each section
    'sphinx.ext.viewcode',  # create html page for each source file and link between it and and the docs

    'sphinxcontrib.bibtex',  # allow bib style citation
    'myst_parser',  # allow Markdown text, e.g., for documents from the GitHub repository
    'enum_tools.autoenum',  # automatically document enums
    'sphinx_toolbox.more_autodoc.autonamedtuple',  # automatically document namedtuples
    'nbsphinx',  # use Jupyter notebooks to add programmatically created visuals
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store', '.tools']

add_module_names = False

todo_include_todos = True

autoclass_content = 'both'

autodoc_typehints = 'signature'

autodoc_typehints_format = 'short'

python_use_unqualified_type_names = True  # workaround, see https://github.com/sphinx-doc/sphinx/issues/10290


def rework_annotations(app, obj, bound_method):
    if "return" in obj.__annotations__ and obj.__annotations__["return"] is None:
        del obj.__annotations__["return"]  # drop return none


def setup(app):
    app.connect("autodoc-before-process-signature", rework_annotations)


# -- Options for HTML output -------------------------------------------------

html_theme = "sphinx_rtd_theme"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

html_css_files = [
    'css/custom.css',
]

# html_style = 'css/custom.css'

html_logo = "../logos/conflowgen_logo_small.png"

html_favicon = "../logos/conflowgen_logo_favicon.png"

# -- Options for formula -----------------------------------------------------


mathjax3_config = {
    'tex2jax': {
        'inlineMath': [["\\(", "\\)"]],
        'displayMath': [["\\[", "\\]"]],
    },
}

# -- Options for Linking  ----------------------------------------------------

version_link = f"{sys.version_info.major}.{sys.version_info.minor}"
intersphinx_mapping = {
    'python': (f'https://docs.python.org/{version_link}', None),  # link to used Python version
    'numpy': ('https://numpy.org/doc/stable/', None),  # link to numpy
}

# -- Options for Included Jupyter Notebooks ----------------------------------

nbsphinx_execute = "always"

nbsphinx_execute_arguments = [
    "--InlineBackend.figure_formats={'svg', 'pdf'}",
    "--InlineBackend.rc=figure.dpi=96",
]

nbsphinx_kernel_name = 'python3'  # always use python3 kernel, even if a different one is used in the notebook

# -- Options for Citing Sources -----------------------------------------------

bibtex_bibfiles = ['references.bib']

bibtex_reference_style = "author_year"

# -- Options for Referencing Figures ------------------------------------------

numfig = True

# -- Style nbsphinx notebook rendering ----------------------------------------
nbsphinx_prolog = """
.. raw:: html

    <style>
        /* Hide the prompts, i.e. the leading numbers in square brackets of Jupyter Notebooks such as '[1]' */
        .nbinput .prompt,
        .nboutput .prompt {
            display: none;
        }

        /* Set output in gray to distinguish it from the remaining Jupyter Notebook */
        div.nboutput.container {
            background-color: #efefef;
        }

        /* Add some white space between the input cell and the remaining cells, especially to the output */
        div.nbinput {
            padding-top: 5px;
            padding-bottom: 5px;
        }

        /* Some of the log statements are too long and a scrolling bar appears. This needs to be avoided */
        div#Generate-the-data pre {
            white-space: pre-wrap !important;
        }

    </style>
"""

# -- Setting up git lfs if Missing ---------------------------------------------


def _install_git_lfs_on_linux_on_the_fly() -> str:
    """
    A dirty hack as there is no clean way how to install git lfs on Read the Docs at the moment.
    """
    _git_lfs_cmd = "./git-lfs"
    if os.path.isfile(_git_lfs_cmd):
        return _git_lfs_cmd

    os.system("echo 'Installing git-lfs on-the-fly'")
    version = 'v3.2.0'
    file_to_download = f'git-lfs-linux-amd64-{version}.tar.gz'
    folder_inside_file = f"git-lfs-{version[1:]}"
    if not os.path.isfile(file_to_download):
        os.system(
            f'wget https://github.com/git-lfs/git-lfs/releases/download/{version}/{file_to_download}'
        )  # download git lfs
    os.system(f'tar xvfz {file_to_download} -C ./.tools')  # extract to ./.tools subdirectory
    os.system(f'ls ./.tools/')
    os.system(f'ls ./.tools/{folder_inside_file}')
    os.system(f'cp ./.tools/{folder_inside_file}/git-lfs ./git-lfs')  # take command (don't care about readme etc.)
    os.system('./git-lfs install')  # make lfs available in current repository
    os.system("echo 'git-lfs is installed'")
    return _git_lfs_cmd


if os.environ.get("IS_RTD", False):
    os.system("echo 'We are currently on the Read-the-Docs server (or somebody just set IS_RTD to true)'")
    git_lfs_cmd = _install_git_lfs_on_linux_on_the_fly()
    os.system("echo 'Fetching sqlite databases'")
    os.system(
        f"yes | {git_lfs_cmd} fetch -p -I '**/notebooks/data/prepared_dbs/*.sqlite'"
    )  # download sqlite databases from remote, say yes to trusting certs
    os.system("echo 'Start checking out the file'")
    os.system(f'{git_lfs_cmd} checkout')  # Replace SQLite database LFS references with the actual files
    os.system("echo 'Checkout finished'")

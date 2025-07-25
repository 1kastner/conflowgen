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

from docutils import nodes
from sphinx.addnodes import pending_xref
from sphinx.application import Sphinx
from sphinx.environment import BuildEnvironment
from sphinx.ext.intersphinx import missing_reference

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
    'sphinx.ext.viewcode',  # create html page for each source file and link between it and the docs

    # sphinx extensions from other Python packages
    'sphinxcontrib.bibtex',  # allow bib style citation
    'myst_parser',  # allow Markdown text, e.g., for documents from the GitHub repository
    'enum_tools.autoenum',  # automatically document enums
    'sphinx_toolbox.more_autodoc.autonamedtuple',  # automatically document namedtuples
    'nbsphinx',  # use Jupyter notebooks to add programmatically created visuals
    'sphinx_last_updated_by_git',  # Extension to display the last update timestamp and author in the documentation
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    'Thumbs.db', '.DS_Store',  # OS-specific
    '_build',  # Sphinx-specific
    '.tools',  # project-specific
    '**.ipynb_checkpoints', '**.virtual_documents'  # specific for Jupyter Notebooks
]

add_module_names = False

todo_include_todos = True  # this is currently especially the open tickets at plotly

autoclass_content = 'both'  # report both the class docs and __init__ docs

autodoc_typehints = 'description'  # show typehints in description, not signature

autodoc_typehints_format = 'short'  # drop leading package path as it takes too much space

python_use_unqualified_type_names = True  # workaround, see https://github.com/sphinx-doc/sphinx/issues/10290

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
    'numpy': ('https://numpy.org/doc/stable', None),
    'matplotlib': ('https://matplotlib.org/stable', None),
    'plotly': ('https://plotly.com/python-api-reference', None),
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

nbsphinx_prolog = r"""
{% set docname = 'docs/' + env.doc2path(env.docname, base=None)|string %}
.. raw:: html

    <!-- nbsphinx prolog - start -->

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
        div pre {
            white-space: pre-wrap !important;
        }
        
        /* Add listing symbol (without this, the template does not create a proper list but just paragraphs) */
        ul.simple>li {
            list-style: square;
            margin: 20px;
        }

    </style>
    
    <div class="admonition note">
        This page was generated from
        <a class="reference external" href="https://github.com/1kastner/conflowgen/blob/main{{ env.config.release|e }}/{{ docname|e }}">
            {{ docname|e }}
        </a>.
    
        Interactive online version:
        <span style="white-space: nowrap;"><a href="https://mybinder.org/v2/gh/1kastner/conflowgen/main{{ env.config.release|e }}?filepath={{ docname|e }}">
            <img alt="Binder badge" src="https://mybinder.org/badge_logo.svg" style="vertical-align:text-bottom"></a>.
        </span>
    
        <a href="{{ env.docname.split('/')|last|e + '.ipynb' }}" class="reference download internal" download>
            Download notebook
        </a>.
    </div>

.. only:: latex

    .. raw:: latex

        \nbsphinxstartnotebook{\scriptsize\noindent\strut
        \textcolor{gray}{The following section was generated from
        \sphinxcode{\sphinxupquote{\strut {{ docname | escape_latex }}}} \dotfill}}
        
        <!-- nbsphinx prolog - end -->
"""


def fix_reference(
    app: Sphinx,
        env: BuildEnvironment,
        node: pending_xref,
        contnode: nodes.TextElement,
) -> nodes.reference | None:
    """
    Fix some intersphinx references that are broken.
    """

    if node["refdomain"] == "py":

        # Replace plotly.graph_objs._figure.Figure with plotly.graph_objects.Figure
        if node["reftarget"] == "plotly.graph_objs._figure.Figure":
            node["reftarget"] = "plotly.graph_objects.Figure"

        return missing_reference(app, env, node, contnode)

    return None


def setup(app: Sphinx) -> None:
    """
    Force sphinx to fix additional things on setup.
    """
    app.connect("missing-reference", fix_reference)


if os.environ.get("IS_RTD", False):
    os.system("echo 'We are currently on the Read-the-Docs server (or somebody just set IS_RTD to true)'")
    os.system("echo 'Fetching SQLite databases'")
    database_names = ["demo_continental_gateway", "demo_deham_cta", "demo_poc"]  # List of database names to download
    sqlite_databases_directory = "notebooks/data/prepared_dbs/"
    os.system("echo 'Current directory:'")
    os.system("pwd")  # Print current directory; we expect to be in the docs folder
    os.makedirs(sqlite_databases_directory, exist_ok=True)  # Create the destination folder if it doesn't exist
    for database_name in database_names:
        os.system(f'echo "Fetching {database_name}"')
        file_url = f'https://media.tuhh.de/mls/software/conflowgen/docs/data/prepared_dbs/{database_name}.sqlite'
        os.system(f'curl -LJO "{file_url}"')
        os.system(f'echo \'mv "{database_name}.sqlite" "{sqlite_databases_directory}"\'')
        os.system(f'mv "{database_name}.sqlite" "{sqlite_databases_directory}"')
    os.system("echo 'SQLite databases fetched'")

    # Kaleido requires Google Chrome to be installed.
    # Either download and install Chrome yourself following Google's instructions for your operating system,
    # or install it from your terminal by running:
    os.system("echo 'Install chrome....'")
    os.system("plotly_get_chrome -y")

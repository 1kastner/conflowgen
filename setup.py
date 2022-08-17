import os.path
from setuptools import setup, find_packages

this_directory = os.path.abspath(os.path.dirname(__file__))

# Load metadata that is also available for the code
metadata = {}
with open(os.path.join(this_directory, "conflowgen", "metadata.py"), encoding="utf-8") as fp:
    exec(fp.read(), metadata)

# Load long description
with open(os.path.join(this_directory, 'Readme.md'), encoding='utf-8') as f:
    long_description = f.read()

# Define actual setup
# noinspection SpellCheckingInspection
setup(
    name='conflowgen',
    version=metadata['__version__'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    url='https://github.com/1kastner/conflowgen',
    python_requires='>=3.8',
    install_requires=[
        # working with distributions and statistics
        'scipy',  # used for, e.g., the lognorm distribution

        # data export
        'numpy',  # used in combination with pandas for column types
        'pandas >=1',  # CSV/Excel import and export
        'openpyxl',  # optional dependency of pandas that is compulsory for xlsx export

        # internal data keeping
        'peewee >=3',  # ORM mapper

        # documentation - decorators used for sphinx but are part of the source code delivered to customers
        'enum_tools >=0.7',  # used for documenting enums via decorators

        # for creating the visuals
        'matplotlib',  # default plots such as bar charts, pie charts, etc.
        'plotly',  # useful for, e.g., Sankey diagrams
        'kaleido',  # plotly depends on this package for exporting its figures, we got this as a present
    ],
    extras_require={
        # Only needed to run the unittests and generate the documentation
        'dev': [
            # testing
            'pytest',  # running the unit tests
            'pytest-cov',  # create coverage report
            'pytest-github-actions-annotate-failures',  # turns pytest failures into action annotations
            'seaborn',  # some visuals in unittests are generated by seaborn
            'nbformat',
            'nbconvert',

            # build documentation
            'sphinx >=5',  # build the documentation
            'sphinx-rtd-theme',  # adding the nice sphinx theme
            'sphinx-toolbox >=v3.2.0b1',  # dependency of enum_tools, we got this as a present
            'myst-parser',  # for Contributing.md
            'sphinxcontrib-bibtex',  # a good help for citing
            'nbsphinx',  # use Jupyter Notebooks in the documentation
            'ipython',  # for setting up the pygments_lexer
            'ipykernel',  # for allowing nbsphinx to execute the Jupyter Notebooks
            'jupyterlab',  # continue development on the Jupyter Notebooks included in this repository

            # checking code quality
            'pylint',  # lint Python code
            'flake8',  # lint Python code
            'flake8_nb <0.5',  # lint Jupyter Notebooks

            # publish at PyPI
            'twine',

            # debug CI
            'watermark'
        ],
        # a collection of nice-to-haves for working on Jupyter Notebooks - just a favorites list of the authors
        'jupyterlab': [
            "jupyterlab-spellchecker",
            "jupyterlab-lsp",
            "python-lsp-server",
            "pyls-flake8",
            "autopep8",
            "rope",
            "yapf",
            "pydocstyle",
            "jupyterlab_code_formatter",
            "black",
            "isort"
        ]
    },
    license=metadata['__license__'],
    author=metadata['__author__'],
    author_email=metadata['__email__'],
    description=metadata['__description__']
)

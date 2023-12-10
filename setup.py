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
            'pytest-xdist',  # use several processes to speed up the testing process
            'pytest-github-actions-annotate-failures',  # turns pytest failures into action annotations
            'seaborn',  # some visuals in unittests are generated by seaborn
            'nbconvert',  # used to run tests in Jupyter notebooks, see ./test/notebooks/test_run_notebooks.py

            # build documentation
            'sphinx',  # build the documentation
            'sphinx-rtd-theme',  # adding the nice sphinx theme
            'sphinx-toolbox',  # dependency of enum_tools, we got this as a present
            'myst-parser',  # for Contributing.md
            'sphinxcontrib-bibtex',  # a good help for citing
            'nbsphinx',  # use Jupyter Notebooks in the documentation
            'ipython',  # for setting up the pygments_lexer
            'ipykernel',  # for allowing nbsphinx to execute the Jupyter Notebooks

            # checking code quality
            'pylint',  # lint Python code
            'flake8',  # lint Python code
            'flake8_nb',  # lint code in Jupyter Notebooks

            # publish at PyPI
            'wheel',  # use command 'bdist_wheel'
            'twine',  # check and upload package to PyPI
        ],
        # a collection of nice-to-haves for working on Jupyter Notebooks - just a favorites list of the authors
        'jupyterlab': [
            'jupyterlab',  # continue development on the Jupyter Notebooks included in this repository
            "jupyterlab-spellchecker",  # avoid typos in documentation
            "jupyterlab-lsp",  # better autocomplete
            "python-lsp-server[all]",  # better autocomplete
        ]
    },
    license=metadata['__license__'],
    author=metadata['__author__'],
    author_email=metadata['__email__'],
    description=metadata['__description__']
)

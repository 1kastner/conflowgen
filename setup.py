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
    install_requires=[
        'pandas',  # CSV/Excel import and export
        'numpy',  # used in combination with pandas for column types
        'openpyxl',  # optional dependency of pandas that is compulsory for xlsx export
        'peewee',  # ORM mapper
        'enum_tools',  # used for documenting enums via decorators

        # for creating the visuals
        'matplotlib',  # default plots such as bar charts, pie charts, etc.
        'plotly',  # useful for e.g. Sankey diagrams
        'seaborn',  # exchanges matplotlib color palletes
        'kaleido',  # plotly depends on this package for SVG export, we got this as a present
    ],
    extras_require={
        # Only needed to run the unittests and generate the documentation
        'dev': [
            # testing
            'pytest',  # running the unit tests
            'pytest-cov',  # create coverage report
            'pytest-github-actions-annotate-failures',  # turns pytest failures into action annotations

            # build documentation
            'sphinx',  # build the documentation
            'sphinx-rtd-theme',  # adding the nice sphinx theme
            'sphinx-toolbox',  # dependency of enum_tools, we got this as a present
            'myst-parser',  # for Contributing.md
            'sphinxcontrib-bibtex',  # a good help for citing
            'sphinx-math-dollar',  # allow writing LaTeX code in math mode using dollar symbols
            'nbsphinx',  # use Jupyter Notebooks in the documentation
            'ipython',  # for setting up the pygments_lexer
            'ipykernel',  # for allowing nbsphinx to execute the Jupyter Notebooks
            'jupyterlab',  # develop the Jupyter Notebooks

            # checking code quality
            'pylint',  # lint Python code
            'flake8',  # lint Python code
            'flake8_nb',  # lint Jupyter Notebooks

            # publish at PyPI
            'twine'
        ]
    },
    license=metadata['__license__'],
    author=metadata['__author__'],
    author_email=metadata['__email__'],
    description=metadata['__description__']
)

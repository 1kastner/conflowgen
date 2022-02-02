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
    name='ConFlowGen',
    version=metadata['__version__'],
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    url='https://github.com/1kastner/conflowgen',
    install_requires=[
        'numpy',
        'pandas',
        'openpyxl',  # optional dependency of pandas that is compulsory for xlsx export
        'peewee',
        'enum_tools',  # used for documenting enums via decorators

        # for creating the visuals
        'matplotlib',
        'plotly',
        'seaborn',
        'kaleido',  # plotly depends on this package for SVG export
    ],
    extras_require={
        # Only needed to run the unittests and generate the documentation
        'dev': [
            # testing
            'pytest',
            'pytest-cov',  # create coverage report
            'pytest-github-actions-annotate-failures',  # turns pytest failures into action annotations

            # build documentation
            'sphinx',
            'sphinx-rtd-theme',
            'sphinx-toolbox',
            'myst-parser',
            'sphinxcontrib-bibtex',
            'sphinx-math-dollar',
            'nbsphinx',
            'jupyterlab',


            # checking code quality
            'pylint',
            'flake8',

            # publish at PyPI
            'twine'
        ]
    },
    license=metadata['__license__'],
    author=metadata['__author__'],
    author_email=metadata['__email__'],
    description='A generator for synthetic container flows at maritime container terminals with a focus is on yard '
                'operations'
)

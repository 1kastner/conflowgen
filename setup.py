from setuptools import setup, find_packages
from os import path

# Load long description
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'Readme.md'), encoding='utf-8') as f:
    long_description = f.read()

# Define actual setup
setup(
    name='ConFlowGen',
    version='0.1',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    url='https://github.com/1kastner/conflowgen',
    install_requires=[
        'numpy',
        'pandas',
        'peewee',
        'enum_tools'  # just used for documentation but is imported in the enum definitions
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
            'sphinx-autodoc-typehints',
            'sphinx-math-dollar',

            # checking code quality
            'pylint',
        ],
        # Only needed when you run the unittests in debug mode or you run the Jupyter Notebooks that create additional
        # visualizations. This is not compulsory though.
        'ui': [
            'plotly',
            'matplotlib',
            'seaborn',
            'kaleido',  # plotly depends on this package for SVG export
        ]
    },
    license='MIT',
    author='Marvin Kastner',
    author_email='marvin.kastner@tuhh.de',
    description='A generator for synthetic container flows at maritime container terminals with a focus is on yard operations'
)

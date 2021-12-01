from setuptools import setup
from os import path

# Load long description
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Define actual setup
setup(
    name='ConFlowGen',
    version='0.1',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=['conflowgen', 'conflowgen.api', 'conflowgen.tools', 'conflowgen.logging',
              'conflowgen.container_flow_data_generation_process',
              'conflowgen.domain_models', 'conflowgen.domain_models.factories', 'conflowgen.domain_models.field_types',
              'conflowgen.domain_models.repositories', 'conflowgen.domain_models.distribution_models',
              'conflowgen.domain_models.distribution_seeders', 'conflowgen.domain_models.distribution_repositories',
              'conflowgen.application_models', 'conflowgen.application_models.repositories',
              'conflowgen.database_connection'],
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
            'pytest',
            'sphinx',
            'sphinx-rtd-theme',
            'sphinx-toolbox',
            'sphinx-autodoc-typehints',
            'sphinx-math-dollar'
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

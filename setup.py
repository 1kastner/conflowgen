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
    license=metadata['__license__'],
    author=metadata['__author__'],
    author_email=metadata['__email__'],
    description=metadata['__description__']
)

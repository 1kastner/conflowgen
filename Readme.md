[![Documentation Status](https://readthedocs.org/projects/conflowgen/badge/?version=latest)](https://conflowgen.readthedocs.io/en/latest/?badge=latest)
[![Docs](https://github.com/1kastner/conflowgen/actions/workflows/docs.yaml/badge.svg)](https://github.com/1kastner/conflowgen/actions/workflows/docs.yaml)
[![Tests](https://github.com/1kastner/conflowgen/actions/workflows/unittests.yaml/badge.svg)](https://github.com/1kastner/conflowgen/actions/workflows/unittests.yaml)
[![codecov](https://codecov.io/gh/1kastner/conflowgen/branch/main/graph/badge.svg?token=GICVMYHJ42)](https://codecov.io/gh/1kastner/conflowgen)
[![Linting](https://github.com/1kastner/conflowgen/actions/workflows/linting.yml/badge.svg)](https://github.com/1kastner/conflowgen/actions/workflows/linting.yml)
[![Demo](https://github.com/1kastner/conflowgen/actions/workflows/demo.yaml/badge.svg)](https://github.com/1kastner/conflowgen/actions/workflows/demo.yaml)
[![Windows conda installation (conda in PATH)](https://github.com/1kastner/conflowgen/actions/workflows/conda-installation.yaml/badge.svg)](https://github.com/1kastner/conflowgen/actions/workflows/conda-installation.yaml)
[![Windows conda installation (conda not in PATH)](https://github.com/1kastner/conflowgen/actions/workflows/conda-installation-not-in-path.yaml/badge.svg)](https://github.com/1kastner/conflowgen/actions/workflows/conda-installation-not-in-path.yaml)

![](./logos/conflowgen_logo_large.png)

# ConFlowGen

The **Con**tainer **Flow** **Gen**erator - a Python application to generate container flows typical for seaport 
container terminals.

## Documentation

A documentation on the background of this project, its API, and a step-by-step guide is available
[at Read the Docs](https://conflowgen.readthedocs.io/en/latest/).
Please check 
[in the background section](https://conflowgen.readthedocs.io/en/latest/background.html)
first whether ConFlowGen is the right tool for your purpose.

## User installation

Please just execute the following lines in a command line interface (CLI) of your choice (e.g., bash, PowerShell, or 
CMD).

```bash
git clone https://github.com/1kastner/conflowgen
cd conflowgen
pip install --user .
```

After you have installed the library, you are ready to define your own scenarios and generate the data.

```python
import conflowgen
database_chooser = conflowgen.DatabaseChooser()
database_chooser.create_new_sqlite_database("new_example.sqlite")
...
```

The next steps from here are described
[in the docs](https://conflowgen.readthedocs.io/en/latest/demo.html).
Further examples exist
[in the demo subdirectory](https://github.com/1kastner/conflowgen/tree/main/demo).

If you wish to execute the Jupyter notebooks that come along the source code, there is an `environment.yml` defined in 
the project root directory. This can be imported by
[default conda commands](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).
For the casual conda user on Windows, the two batch scripts `create-env.bat` and `update-env.bat` exist for managing the environment.
These you can either run on the CLI or just by double-clicking on them.
They do not require any additional user input.
In `create-env.bat`, the conda environment is set up from the `environment.yml`.
Once a while you might want to update the conda environment for which the shortcut is to run `update-env.bat`.

Once the conda environment is set up, you can run JupyterLab in the root directory and navigate to the Jupyter notebooks
that are located in the directories which bear the prefix `visual_`.
This you can either achieve by invoking JupyterLab from the CLI in the project root or, if you are a Windows user, by using `start-jupyterlab.bat`.
This you can either run on the CLI or just by double-clicking on it.
It does not require any additional user input.
When running `start-jupyterlab.bat`, a JupyterLab instance with the project root as its file browser root is started.
In addition, the user settings from `<project-root>/.user-settings` are loaded by default.

## Development installation

For the development installation, instead of simply invoking `pip install` in the CLI in the project root folder, we 
additionally add the optional dependencies `dev` and `ui`.
The dependencies listed in `dev` allow us to run the unit tests and create the documentation.
The dependencies listed in `ui` allow us to create the visuals that are e.g. used when debugging probability-based 
unit tests or when creating visuals in Jupyter notebooks. 

```bash
git clone https://github.com/1kastner/conflowgen
cd conflowgen
pip install --user -e .[dev,ui]
```

### Run all tests

Set up your IDE to use `pytest` in the `tests` subdirectory (relative to the module root directory).
If you use an editor without test support, you can run `python -m pytest ./tests` in the module root directory as well.
Parallel test execution has not been tested and might not work.
If you prefer to also check the test coverage, you can run
`pytest --cov="./conflowgen" --cov-report html`
from the project root directory.
After the execution, the report is located in `<project-root>/htmlcov/index.html`.

### Generate the documentation

For generating the documentation, 
[sphinx](https://www.sphinx-doc.org/)
is used - mostly the default settings are maintained.
The documentation generation process is based on the sphinx boilerplate and the `make` process is unchanged.
To generate the documentation, move to the `docs` subdirectory (relative to the project root folder).
Here, as a Windows user you run `.\make.bat html` from the PowerShell or CMD.

### Checking the code quality

For checking the code quality, pylint and flake8 is used.
Pylint is run by executing `pylint conflowgen` on the project root level.
For flake8, simply invoke `flake8` at the same level.

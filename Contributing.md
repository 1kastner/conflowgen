# Contributing

If you find bugs, errors, omissions or other things that need improvement, please create an issue or a pull request at 
[https://github.com/1kastner/conflowgen/](https://github.com/1kastner/conflowgen/).
Contributions are always welcome!

## Isolating the ConFlowGen development environment

When you work on different tasks related to ConFlowGen, it might be helpful to isolate the development environment from
the other Python environment(s) you use for daily tasks.
This can be achieved e.g. with
[virtualenv](https://virtualenv.pypa.io/en/latest/)
or
[conda](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).

## Development installation

For the development installation, instead of simply invoking `pip install` in the CLI in the project root folder, we 
additionally add the optional dependencies `dev` and `ui`.
Furthermore, an additional dependency on
[pandoc](https://pandoc.org/installing.html)
exists.
The dependencies listed in `dev` allow us to run the unit tests and create the documentation.
The dependencies listed in `ui` allow us to create the visuals that are e.g. used when debugging probability-based 
unit tests or when creating visuals in Jupyter notebooks.

```bash
git clone https://github.com/1kastner/conflowgen
cd conflowgen
pip install -e .[dev,ui]
```

After modification, you can run `run_ci_light.bat` on Windows.
It executes most of the continuous integration (CI) checks that are also automatically executed for GitHub pull requests. 
On GitHub, these are implemented as GitHub workflows.
Once all jobs finish successfully, you can create a pull request if you would like to share your changes with the ConFlowGen community.
Contributions are always welcome!
You can also run the checks individually which is explained in the following.

## Run all tests

Set up your IDE to use `pytest` in the `tests` subdirectory (relative to the module root directory).
If you use an editor without test support, you can run `python -m pytest ./tests` in the module root directory as well.
Parallel test execution has not been tested and might not work.
If you prefer to also check the test coverage, you can run
`pytest --cov="./conflowgen" --cov-report html`
from the project root directory.
After the execution, the test coverage report is located in `<project-root>/htmlcov/index.html`.
Each new feature should be covered by tests unless there are very good reasons why this is not fruitful.

## Generate the documentation

For generating the documentation, 
[sphinx](https://www.sphinx-doc.org/)
is used - mostly the default settings are maintained.
The documentation generation process is based on the sphinx boilerplate and the `make` process is unchanged.
To generate the documentation, move to the `docs` subdirectory (relative to the project root folder).
Here, as a Windows user you run `.\make.bat html` from the PowerShell or CMD.
Linux users invoke `make html` instead.
The landing page of the documentation is created at `<project-root>/docs/_build/html/index.html`.
It is advised to use a strict approach by using the additional argument `SPHINXOPTS="-W --keep-going`
(see the corresponding
[GitHub CI pipeline](https://github.com/1kastner/conflowgen/blob/main/.github/workflows/docs.yaml#L34)
for reference).

## Checking the code quality

For checking the code quality, pylint and flake8 are used.
Pylint is run by executing `pylint conflowgen` and `pylint setup.py` on the project root level.
For flake8, simply invoke `flake8` at the same level.

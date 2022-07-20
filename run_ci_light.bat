@ECHO OFF

ECHO.
ECHO.Please run this batch script as a substitute of the GitHub workflows before creating a pull request. This light
ECHO.version does not run the following CI pipelines:
ECHO.- CodeQL analysis (only used by GitHub)
ECHO.- Installing ConFlowGen in a fresh conda environment (not suitable for repeated invocation)
ECHO.
ECHO.This script needs to be invoked in the development environment (e.g., a virtual environment or a conda
ECHO.environment).
ECHO.

REM run tests
python -m pytest --exitfirst --verbose --failed-first --cov="./conflowgen" --cov-report html || (
    ECHO.Tests failed!
    EXIT /B
)

REM Please check the code coverage!
START "" ./htmlcov/index.html

REM try installation process - as a developer this is the default installation anyways
python -m pip install -e .[dev] || (
    ECHO.Installation failed!
    EXIT /B
)

REM check code quality
flake8 || (
    ECHO.While linting, flake8 failed!
    EXIT /B
)

flake8_nb || (
    ECHO.While linting, flake8_nb failed!
    EXIT /B
)

pylint conflowgen || (
    ECHO.While linting the conflowgen module, pylint failed!
    EXIT /B
)

pylint setup.py || (
    ECHO.While linting setup.py, pylint failed!
    EXIT /B
)

REM build docs
CALL docs/make clean || (
    ECHO.Cleaning up the last built of the documentation failed!
    EXIT /B
)
CALL docs/make html || (
    ECHO.Building the documentation failed!
    EXIT /B
)

REM Please check the docs!
START "" ./docs/_build/html/index.html

REM check the links in the docs
CALL python -m sphinx -W --keep-going ./docs/ ./docs/_build/linkcheck/ -b linkcheck || (
    ECHO.At least one link in the docs is broken!
    EXIT /B
)

ECHO.All steps were executed successfully. Please consider also checking the skipped CI steps manually if you changed
ECHO.related files.

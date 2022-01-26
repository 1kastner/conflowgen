@ECHO OFF

ECHO.Please run this batch script as a substitute of the GitHub workflows before creating a pull request. This light
ECHO.version does not run the following CI pipelines:
ECHO.- CodeQL analysis (only used by GitHub)
ECHO.- Installing ConFlowGen in a fresh conda environment (not suitable for repeated invocation)
ECHO.
ECHO.This script needs to be invoked in the development environment (e.g., a virtual environment or a conda
ECHO.environment).

REM run tests
pytest --exitfirst --verbose --failed-first --cov="./conflowgen" --cov-report html || ECHO.Tests failed && EXIT /B

REM try installation process - as a developer this is the default installation anyways
pip3 install -e .[dev,ui] || ECHO.Installation failed && EXIT /B

REM check code quality
flake8 || ECHO.While linting, flake8 failed && EXIT /B
pylint conflowgen || ECHO.While linting, pylint failed && EXIT /B

REM build docs
CALL docs/make html || ECHO.Building the documentation failed && EXIT /B

REM check the links in the docs
CALL python -m sphinx -W --keep-going ./docs/ ./docs/_build/linkcheck/ -b linkcheck || ECHO.Links in docs broken && EXIT /B

ECHO.All steps were executed successfully. Please consider also checking the skipped CI steps manually if you changed
ECHO.related files.

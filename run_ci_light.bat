@ECHO OFF

ECHO.
ECHO.Please run this batch script as a substitute of the GitHub workflows before creating a pull request. This light
ECHO.version does not run the following CI pipelines:
ECHO.- CodeQL analysis (only used by GitHub)
ECHO.- Installing ConFlowGen from source in a fresh conda environment (not suitable for repeated invocation)
ECHO.
ECHO.This script needs to be invoked in the development environment, e.g., a virtual environment or a conda
ECHO.environment.
ECHO.

ECHO.The following Python interpreter is used:
python -c "import sys; print(sys.base_prefix)"

ECHO.The following sys.prefix is used (typically overwritten by the isolated environment you operate in):
python -c "import sys; print(sys.prefix)"
ECHO.

IF "%VIRTUAL_ENV%" NEQ "" (
    ECHO.Operating inside the virtual environment %VIRTUAL_ENV%
    GOTO START_PIPELINE
)

IF "%CONDA_PREFIX%" NEQ "" (
    ECHO.Operating inside the conda environment %CONDA_PREFIX%
    GOTO START_PIPELINE
)

ECHO.It seems like you are not in an isolated development environment. In a later step, the current version of
ECHO.ConFlowgen will be installed as a library. Please abort if you do not want to clutter your Python installation.
ECHO.If you actually are in an isolated development environment, feel free to improve this check.

:AGAIN
ECHO.
set /p answer="Continue anyway (Y/N)? "
if /i "%answer:~,1%" EQU "Y" goto START_PIPELINE
if /i "%answer:~,1%" EQU "N" exit /b
ECHO.Please type Y for Yes or N for No
GOTO AGAIN

:START_PIPELINE
REM Try the installation process - as a developer this is the default installation anyway
REM This also ships the commands that are used in the latter stages of the pipeline
REM try installation process - as a developer this is the default installation anyways
python -m pip install -e .[dev] || (
    ECHO.Installation failed!
    EXIT /B
)

REM run tests
python -m pytest --exitfirst --verbose --failed-first --cov="./conflowgen" --cov-report html || (
    ECHO.Tests failed!
    EXIT /B
)

REM Please check the code coverage!
START "" ./htmlcov/index.html

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
    ECHO.The linkcheck has spotted an issue, please check!
    EXIT /B
)

ECHO.All steps were executed successfully. Please consider also checking the skipped CI steps manually if you changed
ECHO.related files.

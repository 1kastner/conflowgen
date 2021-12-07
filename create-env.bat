:: Creates the conda environment from the environment file in the same directory

@ECHO OFF

SETLOCAL EnableDelayedExpansion

SET CONDA_ENV=conflowgen

CALL :activate_conda_base

CALL conda info --base >"%~dp0.conda-base.tmp"
SET /p CONDA_BASE=<"%~dp0.conda-base.tmp"
SET CONDA_ENV_DIR="!CONDA_BASE!\envs\%CONDA_ENV%"
ECHO Checking if environment !CONDA_ENV! already exists at !CONDA_ENV_DIR!
IF EXIST !CONDA_ENV_DIR!\ (
    ECHO The environment '!CONDA_ENV!' already exists, a creation is not possible! You might have invoked this script
    ECHO with two intentions:
    ECHO 1^) You want to re-create the environment '!CONDA_ENV!' from scratch. Then remove the environment first with
    ECHO    the corresponding conda command, probably manually remove the folder
    ECHO    !CONDA_ENV_DIR! and afterwards re-invoke this script.
    ECHO 2^) You want to update the environment '!CONDA_ENV!'. Then please use the script 'update_env.bat' located
    ECHO    in the same directory.
    ECHO Conda creation process aborted.
    PAUSE
    GOTO :EOF
) ELSE (
    ECHO No previous installation has been detected, proceed with creation procedure...
)

ECHO Showing information regarding the retrieved conda instance...
CALL conda info

REM Reset errorlevel to 0
VERIFY > nul
ECHO Start creating the environment '!CONDA_ENV!'
CALL conda env create --file "%~dp0environment.yml"
ECHO The environment '!CONDA_ENV!' has been created

IF ERRORLEVEL 1 (
    REM We ended up here because the errorlevel equals 1 or greater, i.e. any type of error
    ECHO The creation process encountered an error, please check the output
    PAUSE
    GOTO :EOF
) ELSE (
    REM This corresponds to the errorlevel of 0, i.e. everything went fine
    ECHO Environment has been created successfully!
    PAUSE
    GOTO :EOF
)

REM End of creation

REM
REM The boilerplate code to activate conda base
REM

:activate_conda_base

    REM Reset errorlevel to 0
    VERIFY > nul

    CALL conda info 1>nul 2>nul
    IF NOT ERRORLEVEL 1 (
        where conda > .conda_path
        SET /p CONDA_PATH= < .conda_path
        ECHO A conda installation located in !CONDA_PATH! is available in your PATH variable and is thus used.
        SET CONDASCRIPTS=!CONDA_PATH!
        GOTO CONDA_FOUND
    )
    ECHO Conda is not available in your PATH. Guessing the location of the installation...

    ECHO Checking in user-specific installations below %USERPROFILE% for which users usually have writing access.
    SET CONDASCRIPTS=%USERPROFILE%\Anaconda3\Scripts\
    ECHO Checking for conda installation at !CONDASCRIPTS!
    IF EXIST %CONDASCRIPTS% (
        GOTO CONDA_FOUND
    )
    SET CONDASCRIPTS=%USERPROFILE%\Miniconda3\Scripts\
    ECHO Checking for conda installation at !CONDASCRIPTS!
    IF EXIST %CONDASCRIPTS% (
        GOTO CONDA_FOUND
    )
    ECHO Checking at computer-wide shared folders for which the user might not have writing access and thus the creation
    ECHO might fail. It is usually preferred if a user-specific installation (i.e. in a folder below %USERPROFILE%)
    ECHO would have been used instead.
    SET CONDASCRIPTS=C:\ProgramData\Anaconda3\Scripts\
    ECHO Checking for conda installation at !CONDASCRIPTS!
    IF EXIST %CONDASCRIPTS% (
        GOTO CONDA_FOUND
    )
    SET CONDASCRIPTS=C:\ProgramData\Miniconda3\Scripts\
    ECHO Checking for conda installation at !CONDASCRIPTS!
    IF EXIST %CONDASCRIPTS% (
        GOTO CONDA_FOUND
    )

    REM We have checked all default paths, nothing else to do than to fail.
    ECHO No conda installation was found. Please install either Anaconda or Miniconda first before invoking this script.
    PAUSE
    EXIT 2

    REM Once a conda installation is found, proceed here
    :CONDA_FOUND
    ECHO The scripts folder at !CONDASCRIPTS! has been detected as a valid conda installation.
    ECHO The conda commands from this directory are used in the following.

    CALL !CONDASCRIPTS! activate base && (
        ECHO The base environment has been activated successfully.
    ) || (
        ECHO The base environment could not be activated. Please check the output for hints.
        PAUSE
        EXIT 2
    )

GOTO :EOF

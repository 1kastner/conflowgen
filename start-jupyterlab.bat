:: Starts JupyterLab

@ECHO OFF

SETLOCAL EnableDelayedExpansion

SET CONDA_ENV=conflowgen

CALL :activate_conda_base

CALL conda activate !CONDA_ENV! || (
    ECHO The environment !CONDA_ENV! could not be activated
    PAUSE
    GOTO :EOF
)

SET JUPYTERLAB_SETTINGS_DIR=%~dp0.user-settings
ECHO Loading settings for JupyterLab from %JUPYTERLAB_SETTINGS_DIR%

REM Reset errorlevel to 0
VERIFY > nul

CALL jupyter lab
IF ERRORLEVEL 1 (
    ECHO JupyterLab encountered an error, please check the error message
    PAUSE
)

REM
REM The boilerplate code to activate conda base
REM

:activate_conda_base

    REM Reset errorlevel to 0
    VERIFY > nul

    CALL conda --info REM >nul 2>nul
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
    SET CONDASCRIPTS=C:\Anaconda3\Scripts\
    ECHO Checking for conda installation at !CONDASCRIPTS!
    IF EXIST %CONDASCRIPTS% (
        GOTO CONDA_FOUND
    )
    SET CONDASCRIPTS=C:\Miniconda3\Scripts\
    ECHO Checking for conda installation at !CONDASCRIPTS!
    IF EXIST %CONDASCRIPTS% (
        GOTO CONDA_FOUND
    )
    SET CONDASCRIPTS=C:\Anaconda\Scripts\
    ECHO Checking for conda installation at !CONDASCRIPTS!
    IF EXIST %CONDASCRIPTS% (
        GOTO CONDA_FOUND
    )
    SET CONDASCRIPTS=C:\Miniconda\Scripts\
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

    CALL !CONDASCRIPTS!activate base && (
        ECHO The base environment has been activated successfully.
    ) || (
        ECHO The base environment could not be activated. Please check the output for hints.
        PAUSE
        EXIT 2
    )

GOTO :EOF

@ECHO OFF

ECHO.
ECHO Delete previously published versions
RMDIR /s build dist *.egg-info
ECHO Deleting finished

ECHO.
ECHO Create files that are meant to be distributed
CALL python setup.py sdist bdist_wheel || PAUSE
ECHO.
ECHO Creation finished

ECHO Checking files that are meant to be distributed
CALL twine check .\dist\*
ECHO.
ECHO Please check whether the twine check passed in all instances.
PAUSE

ECHO.
ECHO Now, you can test the new version by uploading it with the command 'twine upload -r testpypi dist/*'
PAUSE

ECHO.
ECHO Afterwards, you can upload the new version with 'twine upload dist/*'.
PAUSE

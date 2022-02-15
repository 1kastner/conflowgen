# Jupyter Notebook

If you wish to execute the Jupyter notebooks that come along the source code, there is an `environment.yml` defined in 
this directory. This can be imported by
[default conda commands](https://docs.conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html).
For the casual conda user on Windows, the two batch scripts `create-env.bat` and `update-env.bat` exist for managing the
environment.
These you can either run on the CLI or just by double-clicking on them.
They do not require any additional user input.
In `create-env.bat`, the conda environment is set up from the `environment.yml`.
Once a while you might want to update the conda environment for which the shortcut is to run `update-env.bat`.

Once the conda environment is set up, you can run JupyterLab and navigate to the Jupyter notebooks
that are located in the subdirectories.
This you can either achieve by invoking JupyterLab from the CLI or, if you are a Windows user, by using
`start-jupyterlab.bat`.
That script you can start from the CLI or by just double-clicking on it.
It does not require any additional user input.
When running `start-jupyterlab.bat`, a JupyterLab instance with the current folder as its file browser root is started.
In addition, the user settings from `./.user-settings` are loaded by default.

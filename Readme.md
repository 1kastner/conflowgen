[![Documentation Status](https://readthedocs.org/projects/conflowgen/badge/?version=latest)](https://conflowgen.readthedocs.io/en/latest/?badge=latest)
[![Docs](https://github.com/1kastner/conflowgen/actions/workflows/docs.yaml/badge.svg)](https://github.com/1kastner/conflowgen/actions/workflows/docs.yaml)

[![Tests](https://github.com/1kastner/conflowgen/actions/workflows/unittests.yaml/badge.svg)](https://github.com/1kastner/conflowgen/actions/workflows/unittests.yaml)
[![codecov](https://codecov.io/gh/1kastner/conflowgen/branch/main/graph/badge.svg?token=GICVMYHJ42)](https://codecov.io/gh/1kastner/conflowgen)

[![Linting](https://github.com/1kastner/conflowgen/actions/workflows/linting.yml/badge.svg)](https://github.com/1kastner/conflowgen/actions/workflows/linting.yml)
[![CodeFactor](https://www.codefactor.io/repository/github/1kastner/conflowgen/badge)](https://www.codefactor.io/repository/github/1kastner/conflowgen)
[![Language grade: Python](https://img.shields.io/lgtm/grade/python/g/1kastner/conflowgen.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/1kastner/conflowgen/context:python)
[![Total alerts](https://img.shields.io/lgtm/alerts/g/1kastner/conflowgen.svg?logo=lgtm&logoWidth=18)](https://lgtm.com/projects/g/1kastner/conflowgen/alerts/)

[![Demo](https://github.com/1kastner/conflowgen/actions/workflows/demo.yaml/badge.svg)](https://github.com/1kastner/conflowgen/actions/workflows/demo.yaml)
[![Windows conda installation (conda in PATH)](https://github.com/1kastner/conflowgen/actions/workflows/conda-installation.yaml/badge.svg)](https://github.com/1kastner/conflowgen/actions/workflows/conda-installation.yaml)
[![Windows conda installation (conda not in PATH)](https://github.com/1kastner/conflowgen/actions/workflows/conda-installation-not-in-path.yaml/badge.svg)](https://github.com/1kastner/conflowgen/actions/workflows/conda-installation-not-in-path.yaml)

[![DOI](https://zenodo.org/badge/433930077.svg)](https://zenodo.org/badge/latestdoi/433930077)

<table style="border: none">
  <tr style="border: none">
    <td style="border: none">
<img src="./logos/conflowgen_logo_small.png">
    </td>
    <td style="border: none">
      <h1>ConFlowGen</h1>
      The <b>Con</b>tainer <b>Flow</b> <b>Gen</b>erator - a Python application to generate container flows typical for seaport 
container terminals.
    </td>
  </tr>
</table>
  

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
pip install .
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
Examples how to generate synthetic data with ConFlowGen exist
[in the demo subdirectory](https://github.com/1kastner/conflowgen/tree/main/demo).
Additional use cases are presented
[in the example usage subdirectory](https://github.com/1kastner/conflowgen/tree/main/example%20usage).

If you wish to contribute to the project, please have a look at
[Contributing.md](Contributing.md).

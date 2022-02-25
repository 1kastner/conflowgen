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

[![pypi](https://img.shields.io/pypi/v/conflowgen)](https://pypi.org/project/conflowgen/)
[![anaconda](https://img.shields.io/conda/v/mkastner/conflowgen)](https://anaconda.org/mkastner/conflowgen)
[![GitHub](https://img.shields.io/github/v/release/1kastner/conflowgen?label=github)](https://github.com/1kastner/conflowgen/releases)


[![DOI](https://zenodo.org/badge/433930077.svg)](https://zenodo.org/badge/latestdoi/433930077)

<table style="border: none">
  <tr style="border: none">
    <td style="border: none">
<img src="https://raw.githubusercontent.com/1kastner/conflowgen/main/logos/conflowgen_logo_small.png">
    </td>
    <td style="border: none">
      <h1>ConFlowGen</h1>
      The <b>Con</b>tainer <b>Flow</b> <b>Gen</b>erator - a Python application to generate container flows typical for seaport 
container terminals.
    </td>
  </tr>
</table>
  
Please check in the
[background section of the documentation](https://conflowgen.readthedocs.io/en/latest/background.html)
first whether ConFlowGen is the right tool for your purpose.

If you wish to use the module conflowgen, you can install the latest version using pip from the command line interface
(CLI) of your choice (e.g., bash, PowerShell, or CMD).

```bash
pip install conflowgen
```

In addition, conflowgen is also available as a conda package.
However, currently it is depending on several channels.
Please ensure that the channel `conda-forge` has a higher priority than `domdfcoding` (i.e., keep the sequence as shown below).

```bash
conda install -c mkastner -c conda-forge -c domdfcoding conflowgen
```

If you want to download all examples, it is best to obtain a full copy of this repository.
Please ensure that git-lfs is installed to properly download the larger files.
Then, please execute the following lines in your CLI:

```bash
git clone https://github.com/1kastner/conflowgen
cd conflowgen
pip install .
```

After you have installed the module, you are ready to define your own scenarios and generate the data.

```python
import conflowgen
database_chooser = conflowgen.DatabaseChooser()
database_chooser.create_new_sqlite_database("new_example.sqlite")
...
```

The next steps are described
[in the documentation](https://conflowgen.readthedocs.io/en/latest/).

If you use ConFlowGen and decide to publish your results, we would be glad if you mention our work as defined at
https://conflowgen.readthedocs.io/en/latest/background.html/background.html#academic-discussion.

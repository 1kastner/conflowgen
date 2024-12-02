[![Documentation Status](https://readthedocs.org/projects/conflowgen/badge/?version=latest)](https://conflowgen.readthedocs.io/en/latest/?badge=latest)
[![documentation built](https://github.com/1kastner/conflowgen/actions/workflows/docs.yaml/badge.svg)](https://github.com/1kastner/conflowgen/actions/workflows/docs.yaml)
[![CITATION.cff valid](https://github.com/1kastner/conflowgen/actions/workflows/citation.yml/badge.svg)](https://github.com/1kastner/conflowgen/actions/workflows/citation.yml)

[![Tests](https://github.com/1kastner/conflowgen/actions/workflows/unittests.yaml/badge.svg)](https://github.com/1kastner/conflowgen/actions/workflows/unittests.yaml)
[![codecov](https://codecov.io/gh/1kastner/conflowgen/branch/main/graph/badge.svg?token=GICVMYHJ42)](https://codecov.io/gh/1kastner/conflowgen)
[![Linting](https://github.com/1kastner/conflowgen/actions/workflows/linting.yml/badge.svg)](https://github.com/1kastner/conflowgen/actions/workflows/linting.yml)
[![CodeFactor](https://www.codefactor.io/repository/github/1kastner/conflowgen/badge)](https://www.codefactor.io/repository/github/1kastner/conflowgen)

[![Demo](https://github.com/1kastner/conflowgen/actions/workflows/demo.yaml/badge.svg)](https://github.com/1kastner/conflowgen/actions/workflows/demo.yaml)
[![Windows conda installation (conda in PATH)](https://github.com/1kastner/conflowgen/actions/workflows/conda-installation.yaml/badge.svg)](https://github.com/1kastner/conflowgen/actions/workflows/conda-installation.yaml)
[![Windows conda installation (conda not in PATH)](https://github.com/1kastner/conflowgen/actions/workflows/conda-installation-not-in-path.yaml/badge.svg)](https://github.com/1kastner/conflowgen/actions/workflows/conda-installation-not-in-path.yaml)

[![pypi](https://img.shields.io/pypi/v/conflowgen)](https://pypi.org/project/conflowgen/)
[![conda-forge](https://img.shields.io/conda/v/conda-forge/conflowgen?logo=anaconda)](https://anaconda.org/conda-forge/conflowgen)
[![GitHub](https://img.shields.io/github/v/release/1kastner/conflowgen?label=github)](https://github.com/1kastner/conflowgen/releases)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.6447686.svg)](https://zenodo.org/badge/latestdoi/433930077)
[![Install from repository](https://github.com/1kastner/conflowgen/actions/workflows/installation-from-remote.yaml/badge.svg)](https://github.com/1kastner/conflowgen/actions/workflows/installation-from-remote.yaml)

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

In addition, conflowgen is also available on conda-forge.

```bash
conda install -c conda-forge conflowgen
```

If you want to download all examples including simulation models, prepared SQLite databases, and Excel tables, it is best to obtain a full copy of this repository.
Please ensure that 
[git-lfs](https://git-lfs.github.com/)
is installed and properly set up to download the larger files.
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
https://conflowgen.readthedocs.io/en/latest/background.html#presentation-of-conflowgen.

<h1>Jupyter Notebook Tools for Sphinx</h1>

nbsphinx is a Sphinx extension that provides a source parser for *.ipynb files. Custom Sphinx directives are used to show Jupyter Notebook code cells (and of course their results) in both HTML and LaTeX output. Un-evaluated notebooks -- i.e. notebooks without stored output cells -- will be automatically executed during the Sphinx build process.

<b><i>Quick Start:</i></b>

1. Install nbsphinx
2. Edit your conf.py and add 'nbsphinx' to extensions.
3. Edit your index.rst and add the names of your *.ipynb files to the toctree.
4. Run Sphinx!

<b><i>Online documentation (and example of use):</i></b>
https://nbsphinx.readthedocs.io/

<b><i>Source code repository (and issue tracker):</i></b>
https://github.com/spatialaudio/nbsphinx/

<b><i>License:</i></b>
MIT -- see the file LICENSE for details.
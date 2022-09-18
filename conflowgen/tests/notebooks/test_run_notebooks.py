import logging
import os
import unittest
import nbformat
import pytest
from nbconvert.preprocessors import ExecutePreprocessor


class RunNotebooks(unittest.TestCase):

    logger = logging.getLogger("conflowgen")

    @pytest.mark.filterwarnings("ignore::RuntimeWarning")
    def run_jupyter_notebook(self, notebook_filename: str) -> None:
        this_dir = os.path.dirname(os.path.abspath(__file__))
        path_to_notebook = os.path.join(
            this_dir,
            notebook_filename
        )
        with open(path_to_notebook, encoding="utf8") as f:
            nb = nbformat.read(f, as_version=4)

        os.chdir(this_dir)
        self.logger.debug("Execute test in " + os.getcwd())

        ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
        ep.preprocess(nb)

    def test_analyses_with_missing_data(self):
        self.run_jupyter_notebook("analyses_with_missing_data.ipynb")

    def test_previews_with_missing_data(self):
        self.run_jupyter_notebook("previews_with_missing_data.ipynb")

    def test_small_analyses_example(self):
        self.run_jupyter_notebook("fast_analyses_for_proof_of_concept.ipynb")

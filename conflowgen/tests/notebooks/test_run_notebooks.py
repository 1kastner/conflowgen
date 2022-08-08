import os
import unittest
import nbformat
from nbconvert.preprocessors import ExecutePreprocessor


class RunNotebooks(unittest.TestCase):

    @staticmethod
    def run_jupyter_notebook(notebook_filename):
        path_to_notebook = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            notebook_filename
        )
        with open(path_to_notebook, encoding="utf8") as f:
            nb = nbformat.read(f, as_version=4)
        ep = ExecutePreprocessor(timeout=600, kernel_name='python3')
        out = ep.preprocess(nb)
        return out

    def test_analyses_with_missing_data(self):
        self.run_jupyter_notebook("analyses_with_missing_data.ipynb")

    def test_previews_with_missing_data(self):
        self.run_jupyter_notebook("previews_with_missing_data.ipynb")

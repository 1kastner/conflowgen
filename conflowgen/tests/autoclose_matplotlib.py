import unittest

import matplotlib.pyplot as plt


class UnitTestCaseWithMatplotlib(unittest.TestCase):
    def tearDown(self):  # pylint: disable=invalid-name
        plt.close("all")

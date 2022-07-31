import unittest

from conflowgen.tools.theoretical_distribution import ClippedLogNormal


class TestClippedLogNormal(unittest.TestCase):

    def setUp(self) -> None:
        self.cln = ClippedLogNormal(average=5, variance=2, minimum=1, maximum=15)

    def assertArrayEqual(self, a1, a2, msg=""):
        self.assertListEqual(list(a1), list(a2), msg=msg)

    def test_minimum_is_respected(self):
        self.assertArrayEqual(self.cln.get_probabilities([0.5, 4]), [0, 1])
        self.assertArrayEqual(self.cln.get_probabilities([0, 6]), [0, 1])
        self.assertArrayEqual(self.cln.get_probabilities([-2, 5]), [0, 1])

    def test_maximum_is_respected(self):
        self.assertArrayEqual(self.cln.get_probabilities([14, 15.1]), [1, 0])
        self.assertArrayEqual(self.cln.get_probabilities([14, 16]), [1, 0])
        self.assertArrayEqual(self.cln.get_probabilities([14, 100]), [1, 0])

    def test_lognorm_properties(self):
        self.assertAlmostEqual(self.cln._lognorm.mean(), 5)
        self.assertAlmostEqual(self.cln._lognorm.var(), 2)

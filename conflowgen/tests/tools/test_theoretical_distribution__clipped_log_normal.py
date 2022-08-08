import unittest

from conflowgen.tools.continuous_distribution import ClippedLogNormal


class TestClippedLogNormal(unittest.TestCase):

    def setUp(self) -> None:
        self.cln = ClippedLogNormal(average=5, variance=2, minimum=1, maximum=15)

    def assertArrayEqual(self, array_1, array_2, msg=""):  # pylint: disable=invalid-name
        self.assertListEqual(list(array_1), list(array_2), msg=msg)

    def test_minimum_is_respected(self):
        self.assertArrayEqual(self.cln.get_probabilities([0.5, 4]), [0, 1])
        self.assertArrayEqual(self.cln.get_probabilities([0, 6]), [0, 1])
        self.assertArrayEqual(self.cln.get_probabilities([-2, 5]), [0, 1])

    def test_maximum_is_respected(self):
        self.assertArrayEqual(self.cln.get_probabilities([14, 15.1]), [1, 0])
        self.assertArrayEqual(self.cln.get_probabilities([14, 16]), [1, 0])
        self.assertArrayEqual(self.cln.get_probabilities([14, 100]), [1, 0])

    def test_lognorm_properties(self):
        self.assertAlmostEqual(self.cln._lognorm.mean(), 5)  # pylint: disable=protected-access
        self.assertAlmostEqual(self.cln._lognorm.var(), 2)  # pylint: disable=protected-access

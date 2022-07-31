import unittest

from conflowgen.tools.theoretical_distribution import ClippedLogNormal


class TestClippedLogNormal(unittest.TestCase):

    def setUp(self) -> None:
        self.cln = ClippedLogNormal(average=5, variance=2, minimum=1, maximum=15)

    def test_minimum_is_respected(self):
        self.assertEqual(self.cln.get_probability(0.5), 0)
        self.assertEqual(self.cln.get_probability(0), 0)
        self.assertEqual(self.cln.get_probability(-2), 0)

    def test_maximum_is_respected(self):
        self.assertEqual(self.cln.get_probability(15.1), 0)
        self.assertEqual(self.cln.get_probability(16), 0)
        self.assertEqual(self.cln.get_probability(100), 0)

    def test_lognorm_properties(self):
        self.assertAlmostEqual(self.cln._lognorm.mean(), 5)
        self.assertAlmostEqual(self.cln._lognorm.var(), 2)

import unittest

from conflowgen.tools.theoretical_distribution import multiply_discretized_probability_densities


class TestMultiplyDiscretizedProbabilityDensities(unittest.TestCase):

    def test(self):
        a = [0.5, 0.25, 0.25]
        b = [0.3, 0.3, 0.4]
        c = multiply_discretized_probability_densities(a, b)
        self.assertEqual(len(c), 3)
        self.assertAlmostEqual(sum(c), 1)

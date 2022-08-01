import unittest

from conflowgen.tools.theoretical_distribution import multiply_discretized_probability_densities


class TestMultiplyDiscretizedProbabilityDensities(unittest.TestCase):

    def test(self):
        vector_a = [0.5, 0.25, 0.25]
        vector_b = [0.3, 0.3, 0.4]
        vector_c = multiply_discretized_probability_densities(vector_a, vector_b)
        self.assertEqual(len(vector_c), 3)
        self.assertAlmostEqual(sum(vector_c), 1)

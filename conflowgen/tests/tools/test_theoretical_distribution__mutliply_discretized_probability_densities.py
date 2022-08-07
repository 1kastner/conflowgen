import unittest

import numpy as np

from conflowgen.tools.continuous_distribution import multiply_discretized_probability_densities


class TestMultiplyDiscretizedProbabilityDensities(unittest.TestCase):

    def test_default(self):
        vector_a = [0.5, 0.25, 0.25]
        vector_b = [0.3, 0.3, 0.4]
        vector_c = multiply_discretized_probability_densities(vector_a, vector_b)
        self.assertEqual(len(vector_c), 3)
        self.assertAlmostEqual(sum(vector_c), 1)

    def test_with_nan(self):
        vector_a = [0.5, 0.25, 0.25]
        vector_b = [0.3, np.nan, 0.4]
        with self.assertRaises(AssertionError):
            multiply_discretized_probability_densities(vector_a, vector_b)

    def test_with_zeros(self):
        vector_a = [0.5, 0.25, 0.25]
        vector_b = [0, 0, 0]
        vector_c = multiply_discretized_probability_densities(vector_a, vector_b)
        self.assertEqual(len(vector_c), 3)
        self.assertEqual(0, sum(vector_c))

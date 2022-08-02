import unittest

from conflowgen.domain_models.distribution_repositories import normalize_distribution_with_no_dependent_variable


class TestNormalizedDependentDistribution(unittest.TestCase):

    def test_with_normalization(self):
        distribution = {
            "b": 3,
            "c": 2
        }
        with self.assertLogs('conflowgen', level='DEBUG') as context:
            normalized_distribution = normalize_distribution_with_no_dependent_variable(
                distribution,
                values_are_frequencies=True
            )
        self.assertDictEqual(
            normalized_distribution, {
                "b": 0.6,
                "c": 0.4
            }
        )
        self.assertEqual(len(context.output), 1, "Excatly one log message")
        self.assertEqual(
            context.output[0],
            "DEBUG:conflowgen:Sum of fractions was not 1 and was automatically normalized."
        )

    def test_without_normalization(self):
        distribution = {
            "b": 0.6,
            "c": 0.4
        }
        normalized_distribution = normalize_distribution_with_no_dependent_variable(
            distribution,
            values_are_frequencies=True
        )
        self.assertDictEqual(distribution, normalized_distribution)

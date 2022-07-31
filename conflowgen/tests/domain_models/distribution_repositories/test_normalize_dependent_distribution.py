import unittest

from conflowgen.domain_models.distribution_repositories import normalize_distribution_with_one_dependent_variable


class TestNormalizedDependentDistribution(unittest.TestCase):

    def test_simple_case(self):
        distributions = {
            "a": {
                "b": 3,
                "c": 2
            },
            "d": {
                "e": 8,
                "f": 16
            }
        }
        with self.assertLogs('conflowgen', level='DEBUG') as cm:
            normalized_distribution = normalize_distribution_with_one_dependent_variable(
                distributions,
                values_are_frequencies=True
            )
        self.assertDictEqual(
            normalized_distribution, {
                "a": {
                    "b": 0.6,
                    "c": 0.4
                },
                "d": {
                    "e": 1/3,
                    "f": 2/3
                }
            }
        )
        self.assertEqual(len(cm.output), 2)
        self.assertEqual(
            cm.output[0],
            "DEBUG:conflowgen:Sum of fractions was not 1 for 'a' and was automatically normalized."
        )
        self.assertEqual(
            cm.output[1],
            "DEBUG:conflowgen:Sum of fractions was not 1 for 'd' and was automatically normalized."
        )

    def test_mixed_case(self):
        distributions = {
            "a": {
                "b": 0.6,
                "c": 0.4
            },
            "d": {
                "e": 8,
                "f": 16
            }
        }
        with self.assertLogs('conflowgen', level='DEBUG') as cm:
            normalized_distribution = normalize_distribution_with_one_dependent_variable(
                distributions,
                values_are_frequencies=True
            )
        self.assertDictEqual(
            normalized_distribution, {
                "a": {
                    "b": 0.6,
                    "c": 0.4
                },
                "d": {
                    "e": 1/3,
                    "f": 2/3
                }
            }
        )
        self.assertEqual(len(cm.output), 1)
        self.assertEqual(
            cm.output[0],
            "DEBUG:conflowgen:Sum of fractions was not 1 for 'd' and was automatically normalized."
        )

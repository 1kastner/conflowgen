import unittest

from conflowgen.domain_models.distribution_repositories import normalize_nested_distribution


class TestNormalizedNestedDistribution(unittest.TestCase):

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
        normalized_distribution = normalize_nested_distribution(distributions)
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

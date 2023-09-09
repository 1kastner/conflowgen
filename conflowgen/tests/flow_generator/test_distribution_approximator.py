"""
Check if distributions are approximated.
"""

import collections
import unittest

from conflowgen.application.models.random_seed_store import RandomSeedStore
from conflowgen.tools.distribution_approximator import DistributionApproximator, SamplerExhaustedException
from substitute_peewee_database import setup_sqlite_in_memory_db


class TestDistributionApproximator(unittest.TestCase):

    def setUp(self) -> None:
        """Create container database in memory"""
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            RandomSeedStore
        ])

    def test_happy_path(self) -> None:
        """This is the happy path"""
        distribution_approximator = DistributionApproximator({
            "type_1": 1,
            "type_2": 1
        })
        all_samples = [
            distribution_approximator.sample(),
            distribution_approximator.sample()
        ]
        all_samples.sort()
        self.assertEqual(all_samples[0], "type_1")
        self.assertEqual(all_samples[1], "type_2")

    def test_exception(self) -> None:
        """Check if sampler stops once the target destination is reached."""
        distribution_approximator = DistributionApproximator({
            "type_1": 1
        })
        distribution_approximator.sample()
        with self.assertRaises(SamplerExhaustedException):
            distribution_approximator.sample()

    def test_slightly_more_complex(self) -> None:
        """Check if finally from each category sufficient elements are drawn."""
        distribution_approximator = DistributionApproximator({
            "a": 4,
            "b": 2,
            "c": 10
        })
        all_samples = []
        for _ in range(16):  # 4 + 2 + 10
            all_samples.append(distribution_approximator.sample())
        counted_samples = collections.Counter(all_samples)

        self.assertDictEqual(counted_samples, {
            "a": 4,
            "b": 2,
            "c": 10
        })

    def test_from_random_distribution_simple_case(self) -> None:
        """Check if finally from each category sufficient elements are drawn."""
        distribution_approximator = DistributionApproximator.from_distribution({
            "a": 4 / 16,
            "b": 2 / 16,
            "c": 10 / 16
        }, 16)
        all_samples = []
        for _ in range(16):  # 4 + 2 + 10
            all_samples.append(distribution_approximator.sample())
        counted_samples = collections.Counter(all_samples)

        self.assertDictEqual(counted_samples, {
            "a": 4,
            "b": 2,
            "c": 10
        })

    def test_from_random_distribution_complex_case(self) -> None:
        """Check if finally from each category sufficient elements are drawn.
        One of the elements is randomly assigned"""
        distribution_approximator = DistributionApproximator.from_distribution({
            "a": 0.5,
            "b": 0.5
        }, 3)
        all_samples = []
        for _ in range(3):
            all_samples.append(distribution_approximator.sample())
        counted_samples = collections.Counter(all_samples)

        self.assertGreaterEqual(counted_samples["a"], 1)
        self.assertGreaterEqual(counted_samples["b"], 1)
        self.assertEqual(counted_samples["a"] + counted_samples["b"], 3)

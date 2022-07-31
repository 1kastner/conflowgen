import unittest

from conflowgen.domain_models.distribution_models.container_weight_distribution import ContainerWeightDistribution
from conflowgen.domain_models.distribution_repositories import normalize_distribution_with_one_dependent_variable
from conflowgen.domain_models.distribution_repositories.container_weight_distribution_repository import \
    ContainerWeightDistributionRepository
from conflowgen.domain_models.distribution_seeders import container_weight_distribution_seeder
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestContainerWeightDistributionRepository(unittest.TestCase):

    def setUp(self) -> None:
        """Create container database in memory"""
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            ContainerWeightDistribution
        ])
        self.repository = ContainerWeightDistributionRepository()

    def test_seeded_distribution_sums_up_to_one_per_container_length(self):
        container_weight_distribution_seeder.seed()
        container_weight_distribution = self.repository.get_distribution()

        for container_length in ContainerLength:
            distribution_for_container_weights = sum(container_weight_distribution[container_length].values())
            self.assertAlmostEqual(
                distribution_for_container_weights,
                1,
                msg=f"All probabilities must sum to 1, but you only achieved {distribution_for_container_weights}"
            )

    def test_seeded_distribution_values_range_between_zero_to_one(self):
        container_weight_distribution_seeder.seed()
        container_weight_distribution = self.repository.get_distribution()

        for container_length in ContainerLength:
            for container_weight in range(2, 32, 2):
                proportion = container_weight_distribution[container_length][container_weight]
                self.assertGreaterEqual(proportion, 0)
                self.assertLessEqual(proportion, 1)

    def test_distribution_weight_setter(self):
        default_distribution = {
            ContainerLength.twenty_feet: {
                10: 10,
                20: 5
            },
            ContainerLength.forty_feet: {
                10: 15,
                20: 4
            },
            ContainerLength.forty_five_feet: {
                10: 2,
                20: 12
            },
            ContainerLength.other: {
                10: 45,
                20: 8
            }
        }
        normalized_default_distribution = normalize_distribution_with_one_dependent_variable(
            default_distribution,
            values_are_frequencies=True
        )
        self.repository.set_distribution(normalized_default_distribution)
        distribution = self.repository.get_distribution()
        self.assertDictEqual(normalized_default_distribution, distribution)

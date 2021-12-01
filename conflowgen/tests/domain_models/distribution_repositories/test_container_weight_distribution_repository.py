import unittest

from conflowgen.domain_models.distribution_models.container_weight_distribution import ContainerWeightDistribution
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

    def test_distribution_loader_sums_up_to_one_per_container_length(self):
        container_weight_distribution_seeder.seed()
        container_weight_distribution = ContainerWeightDistributionRepository.get_distribution()

        for container_length in ContainerLength:
            distribution_for_container_weights = sum(container_weight_distribution[container_length].values())
            self.assertAlmostEqual(
                distribution_for_container_weights,
                1,
                msg=f"All probabilities must sum to 1, but you only achieved {distribution_for_container_weights}"
            )

    def test_distribution_loader_values_range_between_zero_to_one(self):
        container_weight_distribution_seeder.seed()
        container_weight_distribution = ContainerWeightDistributionRepository.get_distribution()

        for container_length in ContainerLength:
            for container_weight in range(2, 32, 2):
                proportion = container_weight_distribution[container_length][container_weight]
                self.assertGreaterEqual(proportion, 0)
                self.assertLessEqual(proportion, 1)

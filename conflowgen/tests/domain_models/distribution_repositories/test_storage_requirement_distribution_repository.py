import unittest

from conflowgen.domain_models.distribution_models.storage_requirement_distribution import StorageRequirementDistribution
from conflowgen.domain_models.distribution_repositories.storage_requirement_distribution_repository import \
    StorageRequirementDistributionRepository
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.distribution_seeders import storage_requirement_distribution_seeder
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestStorageRequirementDistributionRepository(unittest.TestCase):

    def setUp(self) -> None:
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            StorageRequirementDistribution
        ])
        storage_requirement_distribution_seeder.seed()
        self.repository = StorageRequirementDistributionRepository()

    def test_validity(self):
        distribution = self.repository.get_distribution()
        self.assertSetEqual(set(ContainerLength), set(distribution.keys()))
        for container_length in distribution.keys():
            distribution_for_length = distribution[container_length]
            self.assertSetEqual(set(StorageRequirement), set(distribution_for_length.keys()))
            sum_of_probabilities = sum(distribution_for_length.values())
            self.assertAlmostEqual(sum_of_probabilities, 1)
            for proportion in distribution_for_length.values():
                self.assertGreaterEqual(proportion, 0)
                self.assertLessEqual(proportion, 1)

    def test_set(self):
        distribution = {
            ContainerLength.twenty_feet: {
                StorageRequirement.empty: 0.1,
                StorageRequirement.standard: 0.1,
                StorageRequirement.reefer: 0.2,
                StorageRequirement.dangerous_goods: 0.6
            },
            ContainerLength.forty_feet: {
                StorageRequirement.empty: 0.2,
                StorageRequirement.standard: 0.25,
                StorageRequirement.reefer: 0.2,
                StorageRequirement.dangerous_goods: 0.35
            },
            ContainerLength.forty_five_feet: {
                StorageRequirement.empty: 0.2,
                StorageRequirement.standard: 0.2,
                StorageRequirement.reefer: 0.2,
                StorageRequirement.dangerous_goods: 0.4
            },
            ContainerLength.other: {
                StorageRequirement.empty: 0.25,
                StorageRequirement.standard: 0.4,
                StorageRequirement.reefer: 0.25,
                StorageRequirement.dangerous_goods: 0.1
            }
        }
        self.repository.set_distribution(distribution)
        distribution_2 = self.repository.get_distribution()
        self.assertDictEqual(distribution, distribution_2)

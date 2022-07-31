import unittest

from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.distribution_models.container_dwell_time_distribution import \
    ContainerDwellTimeDistribution
from conflowgen.domain_models.distribution_repositories.container_dwell_time_distribution_repository import \
    ContainerDwellTimeDistributionRepository
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db
from conflowgen.tools.theoretical_distribution import TheoreticalDistribution, ClippedLogNormal
from .example_container_dwell_time_distribution import example_container_dwell_time_distribution


class TestContainerDwellTimeDistributionRepository(unittest.TestCase):

    default_data = example_container_dwell_time_distribution

    def setUp(self) -> None:
        """Create container database in memory"""
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            ContainerDwellTimeDistribution
        ])

    def test_get(self):
        repo = ContainerDwellTimeDistributionRepository()
        repo.set_distributions(
            self.default_data
        )
        distributions = ContainerDwellTimeDistributionRepository().get_distributions()
        for mode_of_transport_i in ModeOfTransport:
            self.assertIn(mode_of_transport_i, distributions.keys())
            for mode_of_transport_j in ModeOfTransport:
                self.assertIn(mode_of_transport_j, distributions[mode_of_transport_i].keys())
                for storage_requirement in StorageRequirement:
                    self.assertIn(storage_requirement, distributions[mode_of_transport_i][mode_of_transport_j].keys())
                    distribution = distributions[mode_of_transport_i][mode_of_transport_j][storage_requirement]

                    distribution_data = self.default_data[mode_of_transport_i][mode_of_transport_j][storage_requirement]

                    self.assertIsInstance(distribution, TheoreticalDistribution)
                    self.assertEqual(distribution.average, distribution_data["average_number_of_hours"])
                    self.assertEqual(distribution.minimum, distribution_data["minimum_number_of_hours"])
                    self.assertEqual(distribution.maximum, distribution_data["maximum_number_of_hours"])

                    self.assertIsInstance(distribution, ClippedLogNormal)
                    self.assertEqual(distribution.variance, distribution_data["variance"])

    def test_set_twice(self):
        repo = ContainerDwellTimeDistributionRepository()
        repo.set_distributions(
            self.default_data
        )
        repo.set_distributions(
            self.default_data
        )

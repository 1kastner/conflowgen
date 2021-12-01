import unittest
import unittest.mock

from conflowgen import ContainerLengthDistributionManager
from conflowgen.domain_models.distribution_models.container_length_distribution import ContainerLengthDistribution
from conflowgen.domain_models.distribution_seeders import container_length_distribution_seeder
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestContainerLengthDistributionManager(unittest.TestCase):

    def setUp(self) -> None:
        """Create container database in memory"""
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            ContainerLengthDistribution
        ])
        container_length_distribution_seeder.seed()
        self.container_length_distribution_manager = ContainerLengthDistributionManager()

    def test_get_container_lengths(self):
        container_lengths = self.container_length_distribution_manager.get_container_lengths()
        for container_length in ContainerLength:
            self.assertIn(container_length, container_lengths.keys())
            container_length_proportion = container_lengths[container_length]
            self.assertLessEqual(container_length_proportion, 1)
            self.assertGreaterEqual(container_length_proportion, 0)
        sum_of_all_proportions = sum(container_lengths.values())
        self.assertAlmostEqual(sum_of_all_proportions, 1)

    def test_set_container_lengths(self):
        with unittest.mock.patch.object(
                self.container_length_distribution_manager,
                'set_container_lengths',
                return_value=None) as mock_method:
            self.container_length_distribution_manager.set_container_lengths({
                ContainerLength.twenty_feet: 0.5,
                ContainerLength.forty_feet: 0.5,
                ContainerLength.forty_five_feet: 0,
                ContainerLength.other: 0
            })
        mock_method.assert_called_once_with({
            ContainerLength.twenty_feet: 0.5,
            ContainerLength.forty_feet: 0.5,
            ContainerLength.forty_five_feet: 0,
            ContainerLength.other: 0
        })

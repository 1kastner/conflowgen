import unittest
import unittest.mock

from conflowgen import ContainerDwellTimeDistributionManager
from conflowgen.domain_models.distribution_seeders import container_dwell_time_distribution_seeder


class TestContainerDwellTimeDistributionManager(unittest.TestCase):

    SAMPLE_DISTRIBUTION = container_dwell_time_distribution_seeder.DEFAULT_CONTAINER_DWELL_TIME_DISTRIBUTIONS

    def setUp(self) -> None:
        self.container_dwell_time_distribution_manager = ContainerDwellTimeDistributionManager()

    def test_get_container_dwell_time_distributions(self):
        with unittest.mock.patch.object(
                self.container_dwell_time_distribution_manager.container_dwell_time_distribution_repository,
                'get_distributions',
                return_value=self.SAMPLE_DISTRIBUTION) as mock_method:
            distribution = self.container_dwell_time_distribution_manager.get_container_dwell_time_distribution()
        mock_method.assert_called_once()
        self.assertEqual(distribution, self.SAMPLE_DISTRIBUTION)

    def test_set_container_dwell_time_distributions(self):
        with unittest.mock.patch.object(
                self.container_dwell_time_distribution_manager.container_dwell_time_distribution_repository,
                'set_distributions',
                return_value=None) as mock_method:
            self.container_dwell_time_distribution_manager.set_container_dwell_time_distribution(
                self.SAMPLE_DISTRIBUTION
            )
        mock_method.assert_called_once_with(self.SAMPLE_DISTRIBUTION)

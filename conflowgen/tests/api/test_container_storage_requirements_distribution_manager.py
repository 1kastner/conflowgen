import unittest
import unittest.mock

from conflowgen import StorageRequirementDistributionManager
from conflowgen.domain_models.distribution_seeders import storage_requirement_distribution_seeder


class TestStorageRequirementsDistributionManager(unittest.TestCase):

    SAMPLE_DISTRIBUTION = storage_requirement_distribution_seeder.DEFAULT_STORAGE_REQUIREMENT_DISTRIBUTION

    def setUp(self) -> None:
        self.manager = StorageRequirementDistributionManager()

    def test_get_container_lengths(self):
        with unittest.mock.patch.object(
                self.manager.storage_requirement_repository,
                'get_distribution',
                return_value=self.SAMPLE_DISTRIBUTION) as mock_method:
            distribution = self.manager.get_storage_requirement_distribution()
        mock_method.assert_called_once()
        self.assertEqual(distribution, self.SAMPLE_DISTRIBUTION)

    def test_set_container_lengths(self):
        with unittest.mock.patch.object(
                self.manager.storage_requirement_repository,
                'set_distribution',
                return_value=None) as mock_method:
            self.manager.set_storage_requirement_distribution(self.SAMPLE_DISTRIBUTION)
        mock_method.assert_called_once_with(self.SAMPLE_DISTRIBUTION)

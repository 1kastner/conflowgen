import unittest
import unittest.mock

from conflowgen import ContainerLengthDistributionManager
from conflowgen.domain_models.data_types.container_length import ContainerLength


class TestContainerLengthDistributionManager(unittest.TestCase):

    SAMPLE_LENGTH_DISTRIBUTION = {
        ContainerLength.twenty_feet: 0.5,
        ContainerLength.forty_feet: 0.5,
        ContainerLength.forty_five_feet: 0,
        ContainerLength.other: 0
    }

    def setUp(self) -> None:
        self.container_length_distribution_manager = ContainerLengthDistributionManager()

    def test_get_container_lengths(self):
        with unittest.mock.patch.object(
                self.container_length_distribution_manager.container_length_repository,
                'get_distribution',
                return_value=self.SAMPLE_LENGTH_DISTRIBUTION) as mock_method:
            distribution = self.container_length_distribution_manager.get_container_lengths()
        mock_method.assert_called_once()
        self.assertEqual(distribution, self.SAMPLE_LENGTH_DISTRIBUTION)

    def test_set_container_lengths(self):
        with unittest.mock.patch.object(
                self.container_length_distribution_manager.container_length_repository,
                'set_distribution',
                return_value=None) as mock_method:
            self.container_length_distribution_manager.set_container_lengths(self.SAMPLE_LENGTH_DISTRIBUTION)
        mock_method.assert_called_once_with(self.SAMPLE_LENGTH_DISTRIBUTION)

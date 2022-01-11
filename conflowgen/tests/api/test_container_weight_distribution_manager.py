import unittest
import unittest.mock

from conflowgen.api.container_weight_distribution_manager import ContainerWeightDistributionManager
from conflowgen.domain_models.data_types.container_length import ContainerLength


class TestContainerWeightDistributionManager(unittest.TestCase):

    CONTAINER_SAMPLE_DISTRIBUTION = {
        ContainerLength.twenty_feet: {
            10: 0.5,
            20: 0.4,
            30: 0.1
        },
        ContainerLength.forty_feet: {
            10: 0.25,
            20: 0.45,
            30: 0.3
        },
    }

    def setUp(self) -> None:
        self.container_weight_distribution_manager = ContainerWeightDistributionManager()

    def test_get_container_weights(self):
        with unittest.mock.patch.object(
                self.container_weight_distribution_manager.container_weight_repository,
                'get_distribution',
                return_value=self.CONTAINER_SAMPLE_DISTRIBUTION) as mock_method:
            self.container_weight_distribution_manager.get_container_weights()
        mock_method.assert_called_once()

    def test_set_container_lengths(self):
        with unittest.mock.patch.object(
                self.container_weight_distribution_manager.container_weight_repository,
                'set_distribution',
                return_value=None) as mock_method:
            self.container_weight_distribution_manager.set_container_weights(self.CONTAINER_SAMPLE_DISTRIBUTION)
        mock_method.assert_called_once_with(self.CONTAINER_SAMPLE_DISTRIBUTION)

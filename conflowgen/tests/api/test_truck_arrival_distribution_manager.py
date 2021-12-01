import unittest
import unittest.mock

from conflowgen import TruckArrivalDistributionManager


class TestTruckArrivalDistributionManager(unittest.TestCase):

    def setUp(self) -> None:
        self.truck_arrival_distribution_manager = TruckArrivalDistributionManager()

    def test_get_truck_arrival_distributions(self):
        with unittest.mock.patch.object(
                self.truck_arrival_distribution_manager.truck_arrival_distribution_repository,
                'get_distribution',
                return_value=None) as mock_method:
            self.truck_arrival_distribution_manager.get_truck_arrival_distributions()
        mock_method.assert_called_once()

    def test_set_truck_arrival_distributions(self):
        distribution = {
            3: .2,
            4: .8
        }
        with unittest.mock.patch.object(
                self.truck_arrival_distribution_manager.truck_arrival_distribution_repository,
                'set_distribution',
                return_value=None) as mock_method:
            self.truck_arrival_distribution_manager.set_truck_arrival_distributions(distribution)
        mock_method.assert_called_once_with(distribution)

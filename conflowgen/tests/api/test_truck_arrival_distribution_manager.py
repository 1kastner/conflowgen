import unittest
import unittest.mock

from conflowgen import TruckArrivalDistributionManager


class TestTruckArrivalDistributionManager(unittest.TestCase):

    ARRIVAL_DISTRIBUTION = {
        3: .2,
        4: .8
    }

    def setUp(self) -> None:
        self.truck_arrival_distribution_manager = TruckArrivalDistributionManager()

    def test_get_truck_arrival_distributions(self):
        with unittest.mock.patch.object(
                self.truck_arrival_distribution_manager.truck_arrival_distribution_repository,
                'get_distribution',
                return_value=self.ARRIVAL_DISTRIBUTION) as mock_method:
            distribution = self.truck_arrival_distribution_manager.get_truck_arrival_distribution()
        mock_method.assert_called_once()
        self.assertEqual(distribution, self.ARRIVAL_DISTRIBUTION)

    def test_set_truck_arrival_distributions(self):

        with unittest.mock.patch.object(
                self.truck_arrival_distribution_manager.truck_arrival_distribution_repository,
                'set_distribution',
                return_value=None) as mock_method:
            self.truck_arrival_distribution_manager.set_truck_arrival_distribution(self.ARRIVAL_DISTRIBUTION)
        mock_method.assert_called_once_with(self.ARRIVAL_DISTRIBUTION)

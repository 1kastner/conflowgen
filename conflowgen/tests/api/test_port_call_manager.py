import datetime
import unittest
import unittest.mock

from conflowgen import PortCallManager
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport


class TestPortCallManager(unittest.TestCase):

    def setUp(self) -> None:
        self.port_call_manager = PortCallManager()

    def test_add_large_scheduled_vehicle(self):
        feeder_service_name = "LX050"
        arrives_at = datetime.date(2021, 7, 9)
        time_of_the_day = datetime.time(hour=11)
        total_capacity = 100
        moved_capacity = 3
        next_destinations = [
            ("DEBRV", 0.6),  # 60% of the containers (in boxes) go here...
            ("RULED", 0.4)  # and the other 40% of the containers (in boxes) go here.
        ]
        with unittest.mock.patch.object(
                self.port_call_manager.schedule_factory,
                'add_schedule',
                return_value=None) as mock_add_schedule:
            with unittest.mock.patch.object(
                    self.port_call_manager,
                    'has_schedule',
                    return_value=False) as mock_has_schedule:
                self.port_call_manager.add_large_scheduled_vehicle(
                    vehicle_type=ModeOfTransport.feeder,
                    service_name=feeder_service_name,
                    vehicle_arrives_at=arrives_at,
                    vehicle_arrives_at_time=time_of_the_day,
                    average_vehicle_capacity=total_capacity,
                    average_moved_capacity=moved_capacity,
                    next_destinations=next_destinations
                )
        mock_has_schedule.assert_called_once_with(
            vehicle_type=ModeOfTransport.feeder,
            service_name=feeder_service_name,
        )
        mock_add_schedule.assert_called_once_with(
            vehicle_type=ModeOfTransport.feeder,
            service_name=feeder_service_name,
            vehicle_arrives_at=arrives_at,
            vehicle_arrives_at_time=time_of_the_day,
            average_vehicle_capacity=total_capacity,
            average_moved_capacity=moved_capacity,
            next_destinations=next_destinations,
            vehicle_arrives_every_k_days=None
        )

    def test_get(self):
        service_name = "123"
        vehicle_type = ModeOfTransport.train
        with unittest.mock.patch.object(
                self.port_call_manager.schedule_factory,
                'get_schedule',
                return_value=True) as mock_method:
            has_schedule = self.port_call_manager.has_schedule(service_name, vehicle_type)
        mock_method.assert_called_once_with(
            service_name,
            vehicle_type
        )
        self.assertTrue(has_schedule)

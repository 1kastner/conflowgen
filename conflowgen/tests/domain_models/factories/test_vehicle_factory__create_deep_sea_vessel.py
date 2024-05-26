import datetime
import unittest

from conflowgen.domain_models.factories.vehicle_factory import UnrealisticValuesException, VehicleFactory
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.vehicle import DeepSeaVessel, LargeScheduledVehicle, Schedule
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestVehicleFactory__create_deep_sea_vessel(unittest.TestCase):  # pylint: disable=invalid-name

    def setUp(self) -> None:
        """Create container database in memory"""
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            DeepSeaVessel,
            LargeScheduledVehicle,
            Schedule
        ])
        self.vehicle_factory = VehicleFactory()

    def test_create_normal_deep_sea_vessel(self) -> None:
        schedule = Schedule.create(
            service_name="LX050",
            vehicle_type=ModeOfTransport.deep_sea_vessel,
            vehicle_arrives_at=datetime.datetime.now(),
            average_vehicle_capacity=800,
            average_inbound_container_volume=50
        )
        self.vehicle_factory.create_deep_sea_vessel(
            capacity_in_teu=800,
            inbound_container_volume=50,
            scheduled_arrival=datetime.datetime.now(),
            schedule=schedule
        )

    def test_create_unrealistic_deep_sea_vessel(self) -> None:
        schedule = Schedule.create(
            service_name="LX050",
            vehicle_type=ModeOfTransport.deep_sea_vessel,
            vehicle_arrives_at=datetime.datetime.now(),
            average_vehicle_capacity=800,
            average_inbound_container_volume=50
        )
        with self.assertRaises(UnrealisticValuesException):
            self.vehicle_factory.create_deep_sea_vessel(
                capacity_in_teu=-1,
                inbound_container_volume=1,
                scheduled_arrival=datetime.datetime.now(),
                schedule=schedule
            )
        with self.assertRaises(UnrealisticValuesException):
            self.vehicle_factory.create_deep_sea_vessel(
                capacity_in_teu=1,
                inbound_container_volume=-1,
                scheduled_arrival=datetime.datetime.now(),
                schedule=schedule
            )
        with self.assertRaises(UnrealisticValuesException):
            self.vehicle_factory.create_deep_sea_vessel(
                capacity_in_teu=50,
                inbound_container_volume=100,
                scheduled_arrival=datetime.datetime.now(),
                schedule=schedule
            )

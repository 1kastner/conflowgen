import datetime
import unittest

from conflowgen.domain_models.factories.vehicle_factory import UnrealisticValuesException, VehicleFactory
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.vehicle import LargeScheduledVehicle, Schedule, Barge
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestVehicleFactory__create_barge(unittest.TestCase):  # pylint: disable=invalid-name

    def setUp(self) -> None:
        """Create container database in memory"""
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            Barge,
            LargeScheduledVehicle,
            Schedule
        ])
        self.vehicle_factory = VehicleFactory()

    def test_create_normal_barge(self) -> None:
        schedule = Schedule.create(
            service_name="LX050",
            vehicle_type=ModeOfTransport.barge,
            vehicle_arrives_at=datetime.datetime.now(),
            average_vehicle_capacity=60,
            average_moved_capacity=30
        )
        self.vehicle_factory.create_barge(
            capacity_in_teu=60,
            moved_capacity=30,
            scheduled_arrival=datetime.datetime.now(),
            schedule=schedule
        )

    def test_create_unrealistic_barge(self) -> None:
        schedule = Schedule.create(
            service_name="LX050",
            vehicle_type=ModeOfTransport.barge,
            vehicle_arrives_at=datetime.datetime.now(),
            average_vehicle_capacity=800,
            average_moved_capacity=50
        )
        with self.assertRaises(UnrealisticValuesException):
            self.vehicle_factory.create_barge(
                capacity_in_teu=-1,
                moved_capacity=1,
                scheduled_arrival=datetime.datetime.now(),
                schedule=schedule
            )
        with self.assertRaises(UnrealisticValuesException):
            self.vehicle_factory.create_barge(
                capacity_in_teu=1,
                moved_capacity=-1,
                scheduled_arrival=datetime.datetime.now(),
                schedule=schedule
            )

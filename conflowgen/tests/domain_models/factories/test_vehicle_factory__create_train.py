import datetime
import unittest

from conflowgen.domain_models.factories.vehicle_factory import UnrealisticValuesException, VehicleFactory
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.vehicle import Train, LargeScheduledVehicle, Schedule
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestVehicleFactory__create_train(unittest.TestCase):  # pylint: disable=invalid-name

    def setUp(self) -> None:
        """Create container database in memory"""
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            Train,
            LargeScheduledVehicle,
            Schedule
        ])
        self.vehicle_factory = VehicleFactory()

    def test_create_normal_train(self) -> None:
        schedule = Schedule.create(
            service_name="LX050",
            vehicle_type=ModeOfTransport.train,
            vehicle_arrives_at=datetime.datetime.now(),
            average_vehicle_capacity=90,
            average_inbound_container_volume=90
        )
        self.vehicle_factory.create_train(
            capacity_in_teu=90,
            inbound_container_volume=90,
            scheduled_arrival=datetime.datetime.now(),
            schedule=schedule
        )

    def test_create_unrealistic_train(self) -> None:
        schedule = Schedule.create(
            service_name="LX050",
            vehicle_type=ModeOfTransport.train,
            vehicle_arrives_at=datetime.datetime.now(),
            average_vehicle_capacity=800,
            average_inbound_container_volume=50
        )
        with self.assertRaises(UnrealisticValuesException):
            self.vehicle_factory.create_train(
                capacity_in_teu=-1,
                inbound_container_volume=1,
                scheduled_arrival=datetime.datetime.now(),
                schedule=schedule
            )

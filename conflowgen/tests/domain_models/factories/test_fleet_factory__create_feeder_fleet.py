"""
Check if containers can be stored in the database, i.e. the ORM model is working.
"""

import datetime
import unittest

from conflowgen.domain_models.factories.fleet_factory import FleetFactory
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.vehicle import Feeder, LargeScheduledVehicle, Schedule
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestVehicleFactory__create_feeder(unittest.TestCase):

    def setUp(self) -> None:
        """Create container database in memory"""
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            Feeder,
            LargeScheduledVehicle,
            Schedule
        ])
        self.fleet_factory = FleetFactory()

    def test_create_feeder_fleet(self) -> None:
        s = Schedule.create(
            service_name="LX050",
            vehicle_type=ModeOfTransport.feeder,
            vehicle_arrives_at=datetime.date(2021, 7, 9),
            vehicle_arrives_at_time=datetime.time(11),
            average_vehicle_capacity=800,
            average_moved_capacity=50
        )
        feeders = self.fleet_factory.create_feeder_fleet(
            schedule=s,
            first_at=datetime.date(2021, 7, 7),
            latest_at=datetime.date(2021, 7, 18)
        )
        self.assertEqual(len(feeders), 2)
        feeder_1 = feeders[0]
        scheduled_arrival_1 = feeder_1.large_scheduled_vehicle.scheduled_arrival
        self.assertEqual(scheduled_arrival_1, datetime.datetime(2021, 7, 9, 11))

        feeder_2 = feeders[1]
        scheduled_arrival_2 = feeder_2.large_scheduled_vehicle.scheduled_arrival
        self.assertEqual(scheduled_arrival_2, datetime.datetime(2021, 7, 16, 11))

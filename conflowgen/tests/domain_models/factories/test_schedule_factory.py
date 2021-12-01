import datetime
import unittest

from conflowgen.domain_models.factories.schedule_factory import ScheduleFactory
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.large_vehicle_schedule import Schedule, Destination
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestScheduleFactory(unittest.TestCase):

    def setUp(self) -> None:
        """Create container database in memory"""
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            Schedule,
            Destination
        ])
        self.schedule_factory = ScheduleFactory()

    def test_add_schedule(self) -> None:
        """Happy path"""
        self.schedule_factory.add_schedule(
            service_name="LX050",
            vehicle_type=ModeOfTransport.feeder,
            vehicle_arrives_at=datetime.date(2021, 7, 9),
            vehicle_arrives_at_time=datetime.time(11),
            average_vehicle_capacity=800,
            average_moved_capacity=1,
            next_destinations=[
                ("DEBRV", 0.5),
                ("CNSHG", 0.5)
            ]
        )

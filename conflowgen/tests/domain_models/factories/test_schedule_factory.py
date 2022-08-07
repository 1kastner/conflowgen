import datetime
import unittest

from peewee import IntegrityError

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
        test_service_name = "LX050"
        self.schedule_factory.add_schedule(
            service_name=test_service_name,
            vehicle_type=ModeOfTransport.feeder,
            vehicle_arrives_at=datetime.date(2021, 7, 9),
            vehicle_arrives_at_time=datetime.time(11),
            average_vehicle_capacity=800,
            average_moved_capacity=1,
            next_destinations=[
                ("DEBRV", 0.6),
                ("CNSHG", 0.4)
            ]
        )
        schedule = Schedule.get_or_none(Schedule.service_name == test_service_name)
        self.assertIsNotNone(schedule)
        self.assertEqual(schedule.vehicle_type, ModeOfTransport.feeder)
        self.assertEqual(schedule.vehicle_arrives_at, datetime.date(2021, 7, 9))
        self.assertEqual(schedule.average_vehicle_capacity, 800)
        self.assertEqual(schedule.average_moved_capacity, 1)
        next_destinations = Destination.select().where(Destination.belongs_to_schedule == schedule)
        next_destinations = list(next_destinations)
        self.assertEqual(len(next_destinations), 2)
        next_destination_names = map(lambda destination: destination.destination_name, next_destinations)
        self.assertSetEqual(set(next_destination_names), {"DEBRV", "CNSHG"})

    def test_repeated_add_schedule(self) -> None:
        test_service_name = "LX050"
        self.schedule_factory.add_schedule(
            service_name=test_service_name,
            vehicle_type=ModeOfTransport.feeder,
            vehicle_arrives_at=datetime.date(2021, 7, 9),
            vehicle_arrives_at_time=datetime.time(11),
            average_vehicle_capacity=800,
            average_moved_capacity=1,
            next_destinations=[
                ("DEBRV", 0.6),
                ("CNSHG", 0.4)
            ]
        )
        with self.assertRaises(IntegrityError):
            self.schedule_factory.add_schedule(
                service_name=test_service_name,
                vehicle_type=ModeOfTransport.feeder,
                vehicle_arrives_at=datetime.date(2021, 7, 10),
                vehicle_arrives_at_time=datetime.time(11),
                average_vehicle_capacity=800,
                average_moved_capacity=1,
                next_destinations=[
                    ("DEBRV", 0.6),
                    ("CNSHG", 0.4)
                ]
            )

    def test_get_schedule(self) -> None:
        test_service_name = "LX050"
        self.schedule_factory.add_schedule(
            service_name=test_service_name,
            vehicle_type=ModeOfTransport.feeder,
            vehicle_arrives_at=datetime.date(2021, 7, 9),
            vehicle_arrives_at_time=datetime.time(11),
            average_vehicle_capacity=800,
            average_moved_capacity=1,
            next_destinations=[
                ("DEBRV", 0.6),
                ("CNSHG", 0.4)
            ]
        )
        schedule = self.schedule_factory.get_schedule(test_service_name, ModeOfTransport.feeder)
        self.assertIsNotNone(schedule)
        self.assertEqual(schedule.vehicle_type, ModeOfTransport.feeder)
        self.assertEqual(schedule.vehicle_arrives_at, datetime.date(2021, 7, 9))
        self.assertEqual(schedule.average_vehicle_capacity, 800)
        self.assertEqual(schedule.average_moved_capacity, 1)
        next_destinations = Destination.select().where(Destination.belongs_to_schedule == schedule)
        next_destinations = list(next_destinations)
        self.assertEqual(len(next_destinations), 2)
        next_destination_names = map(lambda destination: destination.destination_name, next_destinations)
        self.assertSetEqual(set(next_destination_names), {"DEBRV", "CNSHG"})

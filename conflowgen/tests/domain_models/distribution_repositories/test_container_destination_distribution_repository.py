import datetime
import unittest

from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.distribution_repositories.container_destination_distribution_repository import \
    ContainerDestinationDistributionRepository, ContainerDestinationFractionsUnequalOneException
from conflowgen.domain_models.large_vehicle_schedule import Destination, Schedule
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestContainerDestinationDistributionRepository(unittest.TestCase):

    def setUp(self) -> None:
        """Create container database in memory"""
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            Destination,
            Schedule
        ])
        self.repository = ContainerDestinationDistributionRepository()

    def test_empty_destinations(self):
        distribution = self.repository.get_distribution()
        self.assertDictEqual(distribution, {})

    def test_set_distribution(self):
        one_week_later = datetime.datetime.now() + datetime.timedelta(weeks=1)
        schedule = Schedule.create(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeederService",
            vehicle_arrives_at=one_week_later.date(),
            vehicle_arrives_at_time=one_week_later.time(),
            average_vehicle_capacity=300,
            average_inbound_container_volume=300,
            vehicle_arrives_every_k_days=-1
        )
        Schedule.create(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeederServiceIgnored",
            vehicle_arrives_at=one_week_later.date(),
            vehicle_arrives_at_time=one_week_later.time(),
            average_vehicle_capacity=300,
            average_inbound_container_volume=300,
            vehicle_arrives_every_k_days=-1
        )
        destination_1 = Destination.create(
            belongs_to_schedule=schedule,
            sequence_id=1,
            destination_name="TestDestination1",
        )
        destination_2 = Destination.create(
            belongs_to_schedule=schedule,
            sequence_id=2,
            destination_name="TestDestination2",
        )

        distribution = {
            schedule: {
                destination_1: 0.4,
                destination_2: 0.6
            }
        }

        self.repository.set_distribution(distribution)

        all_entries = list(Destination.select())
        self.assertEqual(len(all_entries), 2)

        self.assertEqual(destination_1.fraction, 0.4)
        self.assertEqual(destination_2.fraction, 0.6)

    def test_save_and_load_correspond_for_single_entry(self):
        one_week_later = datetime.datetime.now() + datetime.timedelta(weeks=1)
        schedule = Schedule.create(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeederService",
            vehicle_arrives_at=one_week_later.date(),
            vehicle_arrives_at_time=one_week_later.time(),
            average_vehicle_capacity=300,
            average_inbound_container_volume=300,
            vehicle_arrives_every_k_days=-1
        )
        schedule.save()
        Schedule.create(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeederServiceIgnored",
            vehicle_arrives_at=one_week_later.date(),
            vehicle_arrives_at_time=one_week_later.time(),
            average_vehicle_capacity=300,
            average_inbound_container_volume=300,
            vehicle_arrives_every_k_days=-1
        ).save()
        destination_1 = Destination.create(
            belongs_to_schedule=schedule,
            sequence_id=1,
            destination_name="TestDestination1"
        )
        destination_1.save()
        destination_2 = Destination.create(
            belongs_to_schedule=schedule,
            sequence_id=2,
            destination_name="TestDestination2"
        )
        destination_2.save()

        distribution = {
            schedule: {
                destination_1: 0.4,
                destination_2: 0.6
            }
        }
        self.repository.set_distribution(distribution)
        distribution_retrieved = self.repository.get_distribution()
        self.assertDictEqual(distribution, distribution_retrieved)

    def test_save_and_load_correspond_for_two_entries(self):
        one_week_later = datetime.datetime.now() + datetime.timedelta(weeks=1)
        schedule_1 = Schedule.create(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeederService",
            vehicle_arrives_at=one_week_later.date(),
            vehicle_arrives_at_time=one_week_later.time(),
            average_vehicle_capacity=300,
            average_inbound_container_volume=300,
            vehicle_arrives_every_k_days=-1
        )
        schedule_2 = Schedule.create(
            vehicle_type=ModeOfTransport.deep_sea_vessel,
            service_name="TestDeepSeaVesselService",
            vehicle_arrives_at=one_week_later.date(),
            vehicle_arrives_at_time=one_week_later.time(),
            average_vehicle_capacity=12000,
            average_inbound_container_volume=1000,
            vehicle_arrives_every_k_days=-1
        )
        destination_1 = Destination.create(
            belongs_to_schedule=schedule_1,
            sequence_id=1,
            destination_name="TestFeederDestination1",
            fraction=0.4
        )
        destination_2 = Destination.create(
            belongs_to_schedule=schedule_1,
            sequence_id=2,
            destination_name="TestFeederDestination2",
            fraction=0.6
        )
        destination_3 = Destination.create(
            belongs_to_schedule=schedule_2,
            sequence_id=1,
            destination_name="TestDeepSeaVesselDestination1",
            fraction=0.3
        )
        destination_4 = Destination.create(
            belongs_to_schedule=schedule_2,
            sequence_id=2,
            destination_name="TestDeepSeaVesselDestination2",
            fraction=0.7
        )

        distribution = {
            schedule_1: {
                destination_1: 0.4,
                destination_2: 0.6
            },
            schedule_2: {
                destination_3: 0.3,
                destination_4: 0.7
            }
        }

        distribution_retrieved = self.repository.get_distribution()
        self.assertDictEqual(distribution, distribution_retrieved)

    def test_validator(self):
        one_week_later = datetime.datetime.now() + datetime.timedelta(weeks=1)
        schedule = Schedule.create(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeederService",
            vehicle_arrives_at=one_week_later.date(),
            vehicle_arrives_at_time=one_week_later.time(),
            average_vehicle_capacity=300,
            average_inbound_container_volume=300,
            vehicle_arrives_every_k_days=-1
        )
        Schedule.create(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeederServiceIgnored",
            vehicle_arrives_at=one_week_later.date(),
            vehicle_arrives_at_time=one_week_later.time(),
            average_vehicle_capacity=300,
            average_inbound_container_volume=300,
            vehicle_arrives_every_k_days=-1
        )
        destination_1 = Destination.create(
            belongs_to_schedule=schedule,
            sequence_id=1,
            destination_name="TestDestination1"
        )
        destination_2 = Destination.create(
            belongs_to_schedule=schedule,
            sequence_id=2,
            destination_name="TestDestination2"
        )

        distribution = {
            schedule: {
                destination_1: 0.4,
                destination_2: 0.4
            }
        }

        with self.assertRaises(ContainerDestinationFractionsUnequalOneException):
            self.repository.set_distribution(distribution)

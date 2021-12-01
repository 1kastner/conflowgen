import datetime
import unittest

from conflowgen.domain_models.container import Container
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.large_vehicle_schedule import Schedule, Destination
from conflowgen.domain_models.repositories.large_scheduled_vehicle_repository import LargeScheduledVehicleRepository
from conflowgen.domain_models.vehicle import Train, LargeScheduledVehicle, Truck
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestLargeScheduledVehicleRepository(unittest.TestCase):

    def setUp(self) -> None:
        """Create container database in memory"""
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            Container,
            Schedule,
            LargeScheduledVehicle,
            Train,
            Destination,
            Truck
        ])
        self.lsv_repository = LargeScheduledVehicleRepository()
        self.lsv_repository.set_transportation_buffer(transportation_buffer=0)
        schedule = Schedule.create(
            vehicle_type=ModeOfTransport.train,
            service_name="TestService",
            vehicle_arrives_at=datetime.date(year=2021, month=8, day=7),
            vehicle_arrives_at_time=datetime.time(hour=13, minute=15),
            average_vehicle_capacity=90,
            average_moved_capacity=90,
        )
        self.train_lsv = LargeScheduledVehicle.create(
            capacity_in_teu=90,
            moved_capacity=3,
            scheduled_arrival=datetime.datetime(year=2021, month=8, day=7, hour=13, minute=15),
            schedule=schedule
        )
        self.train_lsv.save()
        self.train = Train.create(
            large_scheduled_vehicle=self.train_lsv
        )
        self.train.save()

    def test_free_capacity_for_one_teu(self):
        Container.create(
            weight=20,
            length=ContainerLength.twenty_feet,
            storage_requirement=StorageRequirement.standard,
            delivered_by=ModeOfTransport.truck,
            picked_up_by=ModeOfTransport.train,
            picked_up_by_initial=ModeOfTransport.feeder,
            picked_up_by_large_scheduled_vehicle=self.train_lsv,
        )

        free_capacity_in_teu = self.lsv_repository.get_free_capacity_for_outbound_journey(self.train)
        self.assertEqual(free_capacity_in_teu, 2)

    def test_free_capacity_for_one_ffe(self):
        Container.create(
            weight=20,
            length=ContainerLength.forty_feet,
            storage_requirement=StorageRequirement.standard,
            delivered_by=ModeOfTransport.truck,
            picked_up_by=ModeOfTransport.train,
            picked_up_by_initial=ModeOfTransport.train,
            picked_up_by_large_scheduled_vehicle=self.train_lsv,
        )

        free_capacity_in_teu = self.lsv_repository.get_free_capacity_for_outbound_journey(self.train)
        self.assertEqual(free_capacity_in_teu, 1)

    def test_free_capacity_for_45_foot_container(self):
        Container.create(
            weight=20,
            length=ContainerLength.forty_five_feet,
            storage_requirement=StorageRequirement.standard,
            delivered_by=ModeOfTransport.truck,
            picked_up_by=ModeOfTransport.train,
            picked_up_by_initial=ModeOfTransport.feeder,
            picked_up_by_large_scheduled_vehicle=self.train_lsv,
        )

        free_capacity_in_teu = self.lsv_repository.get_free_capacity_for_outbound_journey(self.train)
        self.assertEqual(free_capacity_in_teu, 0.75)

    def test_free_capacity_for_other_container(self):
        Container.create(
            weight=20,
            length=ContainerLength.other,
            storage_requirement=StorageRequirement.standard,
            delivered_by=ModeOfTransport.truck,
            picked_up_by=ModeOfTransport.train,
            picked_up_by_initial=ModeOfTransport.feeder,
            picked_up_by_large_scheduled_vehicle=self.train_lsv,
        )

        free_capacity_in_teu = self.lsv_repository.get_free_capacity_for_outbound_journey(self.train)
        self.assertEqual(free_capacity_in_teu, 0.5)

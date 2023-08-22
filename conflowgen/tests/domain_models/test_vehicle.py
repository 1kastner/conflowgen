"""
Check if vehicles can be created.
"""

import datetime
import unittest

from conflowgen.domain_models.arrival_information import \
    TruckArrivalInformationForPickup, TruckArrivalInformationForDelivery
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.large_vehicle_schedule import Schedule
from conflowgen.domain_models.vehicle import Feeder, LargeScheduledVehicle, Truck, Barge
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestTruck(unittest.TestCase):

    def setUp(self) -> None:
        """Create container database in memory"""
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            Truck,
            TruckArrivalInformationForPickup,
            TruckArrivalInformationForDelivery
        ])

    def test_save_truck_delivering_a_container_to_database(self) -> None:
        truck = Truck.create(
            delivers_container=True,
            picks_up_container=False
        )
        self.assertIsNotNone(truck)

    def test_save_truck_picking_up_a_container_to_database(self) -> None:
        ati = TruckArrivalInformationForPickup.create(
            planned_container_pickup_time_prior_berthing=datetime.datetime.now(),
            planned_container_pickup_time_after_initial_storage=None,
            realized_container_pickup_time=datetime.datetime.now() + datetime.timedelta(days=2)
        )
        truck = Truck.create(
            delivers_container=False,
            picks_up_container=True,
            truck_arrival_information_for_pickup=ati
        )
        self.assertIsNotNone(truck)

    def test_repr(self) -> None:
        truck = Truck.create(
            delivers_container=True,
            picks_up_container=False
        )
        self.assertEqual(
            repr(truck),
            "<Truck '1'>"
        )


class TestFeeder(unittest.TestCase):

    def setUp(self) -> None:
        """Create container database in memory"""
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            Feeder,
            LargeScheduledVehicle,
            Schedule,
        ])

    def test_save_feeder_to_database(self) -> None:
        """Check if feeder can be saved"""
        now = datetime.datetime.now()
        schedule = Schedule.create(
            service_name="MyTestFeederLine",
            vehicle_type=ModeOfTransport.feeder,
            vehicle_arrives_at=now,
            average_vehicle_capacity=1100,
            average_moved_capacity=200
        )
        lsv = LargeScheduledVehicle.create(
            vehicle_name="TestFeeder1",
            capacity_in_teu=1000,
            moved_capacity=200,
            scheduled_arrival=now,
            schedule=schedule
        )
        Feeder.create(
            large_scheduled_vehicle=lsv
        )

    def test_repr(self) -> None:
        """Check if feeder can be saved"""
        now = datetime.datetime.now()
        schedule = Schedule.create(
            service_name="MyTestFeederLine",
            vehicle_type=ModeOfTransport.feeder,
            vehicle_arrives_at=now,
            average_vehicle_capacity=1100,
            average_moved_capacity=200
        )
        lsv = LargeScheduledVehicle.create(
            vehicle_name="TestFeeder1",
            capacity_in_teu=1000,
            moved_capacity=200,
            scheduled_arrival=now,
            schedule=schedule
        )
        feeder = Feeder.create(
            large_scheduled_vehicle=lsv
        )
        self.assertEqual(
            repr(feeder),
            "<Feeder: 1>"
        )


class TestBarge(unittest.TestCase):

    def setUp(self) -> None:
        """Create container database in memory"""
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            Barge,
            LargeScheduledVehicle,
            Schedule,
        ])

    def test_save_barge_to_database(self) -> None:
        """Check if barge can be saved"""
        now = datetime.datetime.now()
        schedule = Schedule.create(
            service_name="MyTestBargeLine",
            vehicle_type=ModeOfTransport.barge,
            vehicle_arrives_at=now,
            average_vehicle_capacity=1100,
            average_moved_capacity=200
        )
        lsv = LargeScheduledVehicle.create(
            vehicle_name="TestBarge1",
            capacity_in_teu=1000,
            moved_capacity=200,
            scheduled_arrival=now,
            schedule=schedule
        )
        Barge.create(
            large_scheduled_vehicle=lsv
        )

    def test_repr(self) -> None:
        """Check if barge can be saved"""
        now = datetime.datetime.now()
        schedule = Schedule.create(
            service_name="MyTestBargeLine",
            vehicle_type=ModeOfTransport.barge,
            vehicle_arrives_at=now,
            average_vehicle_capacity=1100,
            average_moved_capacity=200
        )
        lsv = LargeScheduledVehicle.create(
            vehicle_name="TestBarge1",
            capacity_in_teu=1000,
            moved_capacity=200,
            scheduled_arrival=now,
            schedule=schedule
        )
        barge = Barge.create(
            large_scheduled_vehicle=lsv
        )
        self.assertEqual(
            repr(barge),
            "<Barge: 1>"
        )

    def test_get_mode_of_transport(self) -> None:
        """Check if barge can be saved"""
        now = datetime.datetime.now()
        schedule = Schedule.create(
            service_name="MyTestBargeLine",
            vehicle_type=ModeOfTransport.barge,
            vehicle_arrives_at=now,
            average_vehicle_capacity=1100,
            average_moved_capacity=200
        )
        lsv = LargeScheduledVehicle.create(
            vehicle_name="TestBarge1",
            capacity_in_teu=1000,
            moved_capacity=200,
            scheduled_arrival=now,
            schedule=schedule
        )
        barge = Barge.create(
            large_scheduled_vehicle=lsv
        )
        self.assertEqual(
            barge.get_mode_of_transport(),
            ModeOfTransport.barge
        )

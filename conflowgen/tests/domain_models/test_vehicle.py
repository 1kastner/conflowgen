"""
Check if vehicles can be created.
"""

import datetime
import unittest

from conflowgen.domain_models.arrival_information import \
    TruckArrivalInformationForPickup, TruckArrivalInformationForDelivery
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.large_vehicle_schedule import Schedule
from conflowgen.domain_models.vehicle import Feeder, LargeScheduledVehicle, Truck
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
        truck.save()

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
        truck.save()


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
        s = Schedule.create(
            service_name="MyTestFeederLine",
            vehicle_type=ModeOfTransport.feeder,
            vehicle_arrives_at=datetime.datetime.now(),
            average_vehicle_capacity=1100,
            average_moved_capacity=200
        )
        lsv = LargeScheduledVehicle.create(
            capacity_in_teu=1000,
            moved_capacity=200,
            scheduled_arrival=datetime.datetime.now(),
            schedule=s
        )
        feeder = Feeder.create(
            large_scheduled_vehicle=lsv
        )
        feeder.save()

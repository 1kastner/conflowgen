"""
Check if containers can be stored in the database, i.e. the ORM model is working.
"""

import datetime
import unittest

from conflowgen.domain_models.arrival_information import TruckArrivalInformationForDelivery, \
    TruckArrivalInformationForPickup
from conflowgen.domain_models.factories.vehicle_factory import MissingInformationException, \
    UnnecessaryVehicleException, VehicleFactory
from conflowgen.domain_models.vehicle import Truck
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestVehicleFactory__create_truck(unittest.TestCase):

    def setUp(self) -> None:
        """Create container database in memory"""
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            Truck,
            TruckArrivalInformationForPickup,
            TruckArrivalInformationForDelivery
        ])
        self.vehicle_factory = VehicleFactory()

    def test_create_truck_picking_up_a_container_without_arrival_time_information(self) -> None:
        with self.assertRaises(MissingInformationException):
            self.vehicle_factory.create_truck(
                delivers_container=False,
                picks_up_container=True
            )

    def test_create_truck_picking_up_a_container(self) -> None:
        self.vehicle_factory.create_truck(
            delivers_container=False,
            picks_up_container=True,
            truck_arrival_information_for_pickup=TruckArrivalInformationForPickup(
                realized_container_pickup_time=datetime.datetime.now()
            )
        )

    def test_create_truck_delivering_a_container_without_arrival_time_information(self) -> None:
        with self.assertRaises(MissingInformationException):
            self.vehicle_factory.create_truck(
                delivers_container=True,
                picks_up_container=False
            )

    def test_create_truck_delivering_a_container(self) -> None:
        self.vehicle_factory.create_truck(
            delivers_container=True,
            picks_up_container=False,
            truck_arrival_information_for_delivery=TruckArrivalInformationForDelivery(
                realized_container_pickup_time=datetime.datetime.now()
            )
        )

    def test_create_truck_doing_nothing(self) -> None:
        """A truck that neither delivers nor picks up a container is discarded."""
        with self.assertRaises(UnnecessaryVehicleException):
            self.vehicle_factory.create_truck(
                delivers_container=False,
                picks_up_container=False
            )

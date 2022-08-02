"""
Check if containers can be stored in the database, i.e. the ORM model is working.
"""

import unittest

from peewee import IntegrityError

from conflowgen.domain_models.container import Container
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.large_vehicle_schedule import Destination
from conflowgen.domain_models.vehicle import Truck, LargeScheduledVehicle
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestContainer(unittest.TestCase):
    """
    Rudimentarily check if peewee can handle container entries in the database.
    """

    def setUp(self) -> None:
        """Create container database in memory"""
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            Container,
            Truck,
            LargeScheduledVehicle,
            Destination
        ])

    def test_save_to_database(self) -> None:
        """Check if container can be saved"""
        container = Container.create(
            weight=20,
            delivered_by=ModeOfTransport.truck,
            picked_up_by=ModeOfTransport.deep_sea_vessel,
            picked_up_by_initial=ModeOfTransport.feeder,
            length=ContainerLength.twenty_feet,
            storage_requirement=StorageRequirement.standard
        )
        self.assertIsNotNone(container)

    def test_missing_delivered(self) -> None:
        with self.assertRaises(IntegrityError):
            Container.create(
                weight=20,
                delivered_by=None,
                picked_up_by=ModeOfTransport.deep_sea_vessel,
                picked_up_by_initial=ModeOfTransport.deep_sea_vessel,
                length=ContainerLength.twenty_feet,
                storage_requirement=StorageRequirement.standard
            )

    def test_missing_picked_up(self) -> None:
        with self.assertRaises(IntegrityError):
            Container.create(
                weight=20,
                delivered_by=ModeOfTransport.deep_sea_vessel,
                picked_up_by_initial=ModeOfTransport.deep_sea_vessel,
                picked_up_by=None,
                length=ContainerLength.twenty_feet,
                storage_requirement=StorageRequirement.standard
            )

    def test_missing_length(self) -> None:
        with self.assertRaises(IntegrityError):
            Container.create(
                weight=10,
                delivered_by=ModeOfTransport.barge,
                picked_up_by=ModeOfTransport.deep_sea_vessel,
                picked_up_by_initial=ModeOfTransport.deep_sea_vessel,
                length=None,
                storage_requirement=StorageRequirement.dangerous_goods
            )

    def test_missing_storage_requirement(self) -> None:
        with self.assertRaises(IntegrityError):
            Container.create(
                weight=10,
                delivered_by=ModeOfTransport.barge,
                picked_up_by=ModeOfTransport.deep_sea_vessel,
                picked_up_by_initial=ModeOfTransport.deep_sea_vessel,
                length=ContainerLength.forty_feet,
                storage_requirement=None
            )

    def test_container_repr(self) -> None:
        container = Container.create(
            weight=10,
            delivered_by=ModeOfTransport.barge,
            picked_up_by=ModeOfTransport.deep_sea_vessel,
            picked_up_by_initial=ModeOfTransport.deep_sea_vessel,
            length=ContainerLength.forty_feet,
            storage_requirement=StorageRequirement.standard
        )
        representation = repr(container)
        self.assertEqual(
            representation,
            "<Container weight: 10; length: 40 feet; delivered_by_large_scheduled_vehicle: None; "
            "delivered_by_truck: None; picked_up_by_large_scheduled_vehicle: None; picked_up_by_truck: None>"
        )

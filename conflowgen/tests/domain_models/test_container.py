"""
Check if containers can be stored in the database, i.e., the ORM model is working.
"""

import unittest
from dataclasses import dataclass

import parameterized
from peewee import IntegrityError

from conflowgen.descriptive_datatypes import FlowDirection
from conflowgen.domain_models.container import Container, FaultyDataException, NoPickupVehicleException
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.large_vehicle_schedule import Destination
from conflowgen.domain_models.vehicle import Truck, LargeScheduledVehicle
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestContainer(unittest.TestCase):
    """
    Rudimentarily check if peewee can handle container entries in the database.
    Also check whether the class properties work.
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

    def test_faulty_data_exception(self):
        @dataclass
        class BogusModeOfTransport:
            value: int
            name: str

            def __init__(self, value: int, name: str):
                self.value = value
                self.name = name

        mode_of_transport = BogusModeOfTransport(1, "Bogus")

        container = Container.create(
            weight=10,
            delivered_by=mode_of_transport,
            picked_up_by=ModeOfTransport.deep_sea_vessel,
            picked_up_by_initial=ModeOfTransport.deep_sea_vessel,
            length=ContainerLength.forty_feet,
            storage_requirement=StorageRequirement.standard
        )

        with self.assertRaises(FaultyDataException):
            container.get_arrival_time()

    def test_no_pickup_vehicle_exception(self):
        @dataclass
        class BogusModeOfTransport:
            value: int
            name: str

            def __init__(self, value: int, name: str):
                self.value = value
                self.name = name

        mode_of_transport = BogusModeOfTransport(1, "Bogus")

        container = Container.create(
            weight=10,
            delivered_by=ModeOfTransport.barge,
            picked_up_by=mode_of_transport,
            picked_up_by_initial=mode_of_transport,
            length=ContainerLength.forty_feet,
            storage_requirement=StorageRequirement.standard
        )

        with self.assertRaises(NoPickupVehicleException):
            container.get_departure_time()

    @parameterized.parameterized.expand([
        [ContainerLength.twenty_feet, 1],
        [ContainerLength.forty_feet, 2],
        [ContainerLength.forty_five_feet, 2.25],
        [ContainerLength.other, 2.5]
    ])
    def test_occupied_teu(self, container_size, teu):
        """Test whether the container size is correctly converted to TEU"""
        container = Container.create(
            weight=10,
            delivered_by=ModeOfTransport.barge,
            picked_up_by=ModeOfTransport.truck,
            picked_up_by_initial=ModeOfTransport.deep_sea_vessel,
            length=container_size,
            storage_requirement=StorageRequirement.standard
        )
        self.assertEqual(teu, container.occupied_teu)

    @parameterized.parameterized.expand([
        [ModeOfTransport.deep_sea_vessel, ModeOfTransport.deep_sea_vessel, FlowDirection.transshipment_flow],
        [ModeOfTransport.deep_sea_vessel, ModeOfTransport.feeder, FlowDirection.transshipment_flow],
        [ModeOfTransport.feeder, ModeOfTransport.deep_sea_vessel, FlowDirection.transshipment_flow],
        [ModeOfTransport.feeder, ModeOfTransport.feeder, FlowDirection.transshipment_flow],

        [ModeOfTransport.deep_sea_vessel, ModeOfTransport.truck, FlowDirection.import_flow],
        [ModeOfTransport.deep_sea_vessel, ModeOfTransport.barge, FlowDirection.import_flow],
        [ModeOfTransport.deep_sea_vessel, ModeOfTransport.train, FlowDirection.import_flow],
        [ModeOfTransport.feeder, ModeOfTransport.truck, FlowDirection.import_flow],
        [ModeOfTransport.feeder, ModeOfTransport.barge, FlowDirection.import_flow],
        [ModeOfTransport.feeder, ModeOfTransport.train, FlowDirection.import_flow],

        [ModeOfTransport.truck, ModeOfTransport.deep_sea_vessel, FlowDirection.export_flow],
        [ModeOfTransport.truck, ModeOfTransport.feeder, FlowDirection.export_flow],
        [ModeOfTransport.barge, ModeOfTransport.deep_sea_vessel, FlowDirection.export_flow],
        [ModeOfTransport.barge, ModeOfTransport.feeder, FlowDirection.export_flow],
        [ModeOfTransport.train, ModeOfTransport.deep_sea_vessel, FlowDirection.export_flow],
        [ModeOfTransport.train, ModeOfTransport.feeder, FlowDirection.export_flow],

        [ModeOfTransport.truck, ModeOfTransport.truck, FlowDirection.undefined],
        [ModeOfTransport.truck, ModeOfTransport.barge, FlowDirection.undefined],
        [ModeOfTransport.truck, ModeOfTransport.train, FlowDirection.undefined],
        [ModeOfTransport.barge, ModeOfTransport.truck, FlowDirection.undefined],
        [ModeOfTransport.barge, ModeOfTransport.barge, FlowDirection.undefined],
        [ModeOfTransport.barge, ModeOfTransport.train, FlowDirection.undefined],
        [ModeOfTransport.train, ModeOfTransport.truck, FlowDirection.undefined],
        [ModeOfTransport.train, ModeOfTransport.barge, FlowDirection.undefined],
        [ModeOfTransport.train, ModeOfTransport.train, FlowDirection.undefined],
    ])
    def test_flow_direction(self, delivered_by, picked_up_by, container_flow):
        """Test whether all flow directions are detected correctly"""
        container: Container = Container.create(
            weight=10,
            delivered_by=delivered_by,
            picked_up_by=picked_up_by,
            picked_up_by_initial=ModeOfTransport.truck,
            length=ContainerLength.forty_feet,
            storage_requirement=StorageRequirement.standard
        )
        self.assertEqual(container_flow, container.flow_direction)

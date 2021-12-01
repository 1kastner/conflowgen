"""
Check if containers can be stored in the database, i.e. the ORM model is working.
"""

import datetime
import unittest

from conflowgen.domain_models.arrival_information import TruckArrivalInformationForDelivery, \
    TruckArrivalInformationForPickup
from conflowgen.domain_models.container import Container
from conflowgen.domain_models.distribution_models.container_length_distribution import ContainerLengthDistribution
from conflowgen.domain_models.distribution_models.container_weight_distribution import ContainerWeightDistribution
from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.distribution_models.storage_requirement_distribution import StorageRequirementDistribution
from conflowgen.domain_models.distribution_seeders import mode_of_transport_distribution_seeder, \
    container_weight_distribution_seeder, container_length_distribution_seeder, \
    container_storage_requirement_distribution_seeder
from conflowgen.domain_models.factories.container_factory import ContainerFactory
from conflowgen.domain_models.factories.fleet_factory import FleetFactory
from conflowgen.domain_models.factories.vehicle_factory import VehicleFactory
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.large_vehicle_schedule import Destination
from conflowgen.domain_models.vehicle import Feeder, LargeScheduledVehicle, Schedule, Truck
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestContainerFactory(unittest.TestCase):

    def setUp(self) -> None:
        """Create container database in memory"""
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            Schedule,
            Container,
            Truck,
            Feeder,
            LargeScheduledVehicle,
            Schedule,
            ModeOfTransportDistribution,
            ContainerWeightDistribution,
            TruckArrivalInformationForDelivery,
            TruckArrivalInformationForPickup,
            ContainerLengthDistribution,
            Destination,
            StorageRequirementDistribution
        ])
        mode_of_transport_distribution_seeder.seed()
        container_weight_distribution_seeder.seed()
        container_length_distribution_seeder.seed()
        container_storage_requirement_distribution_seeder.seed()

        s = Schedule.create(
            service_name="LX050",
            vehicle_type=ModeOfTransport.feeder,
            vehicle_arrives_at=datetime.date(2021, 7, 9),
            vehicle_arrives_at_time=datetime.time(11),
            average_vehicle_capacity=800,
            average_moved_capacity=1
        )
        feeders = FleetFactory().create_feeder_fleet(
            schedule=s,
            first_at=datetime.date(2021, 7, 7),
            latest_at=datetime.date(2021, 7, 10)
        )
        self.assertEqual(
            len(feeders),
            1
        )
        self.feeder = feeders[0]
        self.container_factory = ContainerFactory()
        self.container_factory.reload_distributions()

    def test_create_containers_for_truck(self) -> None:
        VehicleFactory().create_truck(
            delivers_container=True,
            picks_up_container=False,
            truck_arrival_information_for_delivery=TruckArrivalInformationForDelivery.create(
                realized_container_delivery_time=datetime.datetime.now()
            )
        )
        container = self.container_factory.create_container_for_delivering_truck(
            picked_up_by_large_scheduled_vehicle_subtype=self.feeder
        )

        self.assertEqual(
            container.delivered_by,
            ModeOfTransport.truck
        )
        self.assertEqual(
            container.picked_up_by,
            ModeOfTransport.feeder
        )
        self.assertEqual(
            container.delivered_by_large_scheduled_vehicle,
            None
        )
        self.assertEqual(
            container.picked_up_by_truck,
            None
        )
        self.assertEqual(
            container.picked_up_by_large_scheduled_vehicle,
            self.feeder.large_scheduled_vehicle
        )
        self.assertEqual(
            container.delivered_by_truck,
            None,
            msg="Truck is assigned later"
        )

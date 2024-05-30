import datetime
import unittest

from conflowgen.application.models.random_seed_store import RandomSeedStore
from conflowgen.domain_models.container import Container
from conflowgen.domain_models.distribution_models.container_length_distribution import ContainerLengthDistribution
from conflowgen.domain_models.distribution_models.container_weight_distribution import ContainerWeightDistribution
from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.distribution_models.storage_requirement_distribution import StorageRequirementDistribution
from conflowgen.domain_models.distribution_seeders import mode_of_transport_distribution_seeder, \
    container_weight_distribution_seeder, container_length_distribution_seeder, \
    storage_requirement_distribution_seeder
from conflowgen.domain_models.factories.container_factory import ContainerFactory
from conflowgen.domain_models.factories.fleet_factory import FleetFactory
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.large_vehicle_schedule import Destination
from conflowgen.domain_models.vehicle import Feeder, LargeScheduledVehicle, Schedule, Truck, DeepSeaVessel
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestContainerFactory(unittest.TestCase):

    def setUp(self) -> None:
        """Create container database in memory"""
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            Feeder,
            DeepSeaVessel,
            LargeScheduledVehicle,
            Schedule,
            Container,
            Truck,
            ModeOfTransportDistribution,
            ContainerWeightDistribution,
            ContainerLengthDistribution,
            Destination,
            StorageRequirementDistribution,
            RandomSeedStore
        ])
        mode_of_transport_distribution_seeder.seed()
        container_weight_distribution_seeder.seed()
        container_length_distribution_seeder.seed()
        storage_requirement_distribution_seeder.seed()

        schedule = Schedule.create(
            service_name="LX050",
            vehicle_type=ModeOfTransport.feeder,
            vehicle_arrives_at=datetime.date(2021, 7, 9),
            vehicle_arrives_at_time=datetime.time(11),
            average_vehicle_capacity=800,
            average_inbound_container_volume=3
        )
        self.feeders = FleetFactory().create_feeder_fleet(
            schedule=schedule,
            first_at=datetime.date(2021, 7, 7),
            latest_at=datetime.date(2021, 7, 18)
        )
        self.assertEqual(
            len(self.feeders),
            2
        )
        self.container_factory = ContainerFactory()
        self.container_factory.reload_distributions()

    def test_create_containers_for_feeder_vessel(self) -> None:
        feeder_1 = self.feeders[1]

        # noinspection PyTypeChecker
        containers = self.container_factory.create_containers_for_large_scheduled_vehicle(feeder_1)

        self.assertEqual(
            1,
            len(containers),
            "a single container should be generated"
        )
        self.assertEqual(
            containers[0].delivered_by,
            ModeOfTransport.feeder
        )
        self.assertEqual(
            containers[0].delivered_by_large_scheduled_vehicle,
            feeder_1.large_scheduled_vehicle
        )
        self.assertIsNone(containers[0].delivered_by_truck)

    def test_create_containers_for_single_deep_sea_vessel_during_ramp_up_period(self):
        schedule = Schedule.create(
            service_name="SunExpress",
            vehicle_type=ModeOfTransport.deep_sea_vessel,
            vehicle_arrives_at=datetime.date(2021, 7, 9),
            vehicle_arrives_at_time=datetime.time(11),
            average_vehicle_capacity=24000,
            average_inbound_container_volume=3000
        )
        vessels = FleetFactory().create_deep_sea_vessel_fleet(
            schedule=schedule,
            first_at=datetime.date(2021, 7, 8),
            latest_at=datetime.date(2021, 7, 10)
        )
        self.assertEqual(
            len(vessels),
            1
        )
        vessel = vessels[0]

        self.container_factory.set_ramp_up_and_down_times(
            ramp_up_period_end=datetime.datetime(2021, 7, 10),
            ramp_down_period_start=None
        )

        # noinspection PyTypeChecker
        containers = self.container_factory.create_containers_for_large_scheduled_vehicle(vessel)

        container_volume = sum(c.occupied_teu for c in containers)

        self.assertGreater(container_volume, 2900, "A bit less than 3000 is acceptable but common!")
        self.assertLess(container_volume, 3100, "A bit more than 3000 is acceptable but common!")

    def test_create_containers_for_single_deep_sea_vessel_during_ramp_down_period(self):
        schedule = Schedule.create(
            service_name="SunExpress",
            vehicle_type=ModeOfTransport.deep_sea_vessel,
            vehicle_arrives_at=datetime.date(2024, 7, 9),
            vehicle_arrives_at_time=datetime.time(11),
            average_vehicle_capacity=24000,
            average_inbound_container_volume=3000
        )
        vessels = FleetFactory().create_deep_sea_vessel_fleet(
            schedule=schedule,
            first_at=datetime.date(2024, 7, 8),
            latest_at=datetime.date(2024, 7, 10)
        )
        self.assertEqual(
            len(vessels),
            1
        )
        vessel = vessels[0]

        self.container_factory.set_ramp_up_and_down_times(
            ramp_up_period_end=None,
            ramp_down_period_start=datetime.datetime(2024, 7, 8)
        )

        # noinspection PyTypeChecker
        containers = self.container_factory.create_containers_for_large_scheduled_vehicle(vessel)

        container_volume_in_teu = sum(c.occupied_teu for c in containers)

        self.assertGreater(container_volume_in_teu, 500, "A bit less than 600 is acceptable but common!")
        self.assertLess(container_volume_in_teu, 700, "A bit more than 600 is acceptable but common!")

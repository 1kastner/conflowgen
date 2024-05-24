import datetime
import unittest

from conflowgen import PortCallManager
from conflowgen.application.models.container_flow_generation_properties import ContainerFlowGenerationProperties
from conflowgen.application.models.random_seed_store import RandomSeedStore
from conflowgen.application.repositories.container_flow_generation_properties_repository import \
    ContainerFlowGenerationPropertiesRepository
from conflowgen.database_connection.create_tables import create_tables
from conflowgen.domain_models.container import Container
from conflowgen.domain_models.distribution_models.container_dwell_time_distribution import \
    ContainerDwellTimeDistribution
from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.distribution_models.storage_requirement_distribution import StorageRequirementDistribution
from conflowgen.domain_models.distribution_seeders import mode_of_transport_distribution_seeder, \
    seed_all_distributions, container_dwell_time_distribution_seeder
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.vehicle import Feeder, DeepSeaVessel
from conflowgen.flow_generator.container_flow_generation_service import \
    ContainerFlowGenerationService
from conflowgen.domain_models.large_vehicle_schedule import Schedule
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestContainerFlowGeneratorService__generate(unittest.TestCase):  # pylint: disable=invalid-name

    def setUp(self) -> None:
        """Create container database in memory"""
        self.sqlite_db = setup_sqlite_in_memory_db()
        self.sqlite_db.create_tables([
            ContainerFlowGenerationProperties,
            ModeOfTransportDistribution,
            Schedule,
            StorageRequirementDistribution,
            ContainerDwellTimeDistribution,
            RandomSeedStore,
        ])
        mode_of_transport_distribution_seeder.seed()
        container_dwell_time_distribution_seeder.seed()

        container_flow_generation_properties_manager = ContainerFlowGenerationPropertiesRepository()
        properties = container_flow_generation_properties_manager.get_container_flow_generation_properties()
        properties.name = "Demo file"
        properties.start_date = datetime.datetime.now().date()
        properties.end_date = datetime.datetime.now().date() + datetime.timedelta(days=21)
        container_flow_generation_properties_manager.set_container_flow_generation_properties(properties)

        self.container_flow_generator_service = ContainerFlowGenerationService()

    def test_happy_path_no_mocking(self):
        create_tables(self.sqlite_db)
        seed_all_distributions()
        port_call_manager = PortCallManager()
        port_call_manager.add_vehicle(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeeder",
            vehicle_arrives_at=datetime.date(2021, 7, 9),
            vehicle_arrives_at_time=datetime.time(11),
            average_vehicle_capacity=800,
            average_moved_capacity=100,
            next_destinations=None
        )
        port_call_manager.add_vehicle(
            vehicle_type=ModeOfTransport.deep_sea_vessel,
            service_name="TestDeepSeaVessel",
            vehicle_arrives_at=datetime.date(2021, 7, 9),
            vehicle_arrives_at_time=datetime.time(11),
            average_vehicle_capacity=800,
            average_moved_capacity=100,
            next_destinations=None
        )
        self.container_flow_generator_service.generate()

    def test_nothing_to_do(self):
        create_tables(self.sqlite_db)
        seed_all_distributions()
        self.container_flow_generator_service.generate()

    def test_happy_path_no_mocking_with_ramp_up_and_ramp_down(self):
        create_tables(self.sqlite_db)
        seed_all_distributions()

        container_flow_generation_properties_manager = ContainerFlowGenerationPropertiesRepository()
        properties: ContainerFlowGenerationProperties = (container_flow_generation_properties_manager
                                                         .get_container_flow_generation_properties())
        properties.ramp_up_period = 5
        properties.ramp_down_period = 5
        container_flow_generation_properties_manager.set_container_flow_generation_properties(properties)

        port_call_manager = PortCallManager()
        port_call_manager.add_vehicle(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeeder",
            vehicle_arrives_at=properties.start_date + datetime.timedelta(days=3),
            vehicle_arrives_at_time=datetime.time(11),
            average_vehicle_capacity=800,
            average_moved_capacity=100,
            next_destinations=None
        )
        port_call_manager.add_vehicle(
            vehicle_type=ModeOfTransport.deep_sea_vessel,
            service_name="TestDeepSeaVessel",
            vehicle_arrives_at=properties.start_date + datetime.timedelta(days=8),
            vehicle_arrives_at_time=datetime.time(11),
            average_vehicle_capacity=12000,
            average_moved_capacity=1000,
            next_destinations=None
        )
        port_call_manager.add_vehicle(
            vehicle_type=ModeOfTransport.deep_sea_vessel,
            service_name="TestDeepSeaVessel2",
            vehicle_arrives_at=properties.end_date - datetime.timedelta(days=2),
            vehicle_arrives_at_time=datetime.time(11),
            average_vehicle_capacity=12000,
            average_moved_capacity=1000,
            next_destinations=None
        )
        self.container_flow_generator_service.generate()

        reference = list(Container.select())

        # Vehicle 1 - inbound during ramp-up untouched
        feeder = Feeder.select().where(
            Feeder.large_scheduled_vehicle.name == "TestFeeder"
        )
        feeder_instance = list(feeder)[0]
        number_containers_during_ramp_up = Container.select().where(
            Container.delivered_by_large_scheduled_vehicle == feeder
        ).count()
        self.assertLess(
            number_containers_during_ramp_up,
            100
        )
        self.assertGreater(
            number_containers_during_ramp_up,
            50
        )

        # Vehicle 2 - no effect
        deep_sea_vessel_1 = DeepSeaVessel.select().where(
            DeepSeaVessel.large_scheduled_vehicle.name == "TestDeepSeaVessel"
        )
        number_containers_in_normal_phase = Container.select().where(
            Container.picked_up_by_large_scheduled_vehicle == deep_sea_vessel_1
        ).count()
        self.assertLess(
            number_containers_in_normal_phase,
            1000
        )
        self.assertGreater(
            number_containers_in_normal_phase,
            500
        )

        # Vehicle 3 - inbound volume during ramp-down throttled
        deep_sea_vessel_2 = DeepSeaVessel.select().where(
            DeepSeaVessel.large_scheduled_vehicle.name == "TestDeepSeaVessel2"
        )
        number_containers_during_ramp_down = Container.select().where(
            Container.delivered_by_large_scheduled_vehicle == deep_sea_vessel_2
        ).count()
        self.assertLess(
            number_containers_during_ramp_down,
            1000
        )
        self.assertGreater(
            number_containers_during_ramp_down,
            500
        )

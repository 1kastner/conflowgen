import datetime
import unittest

from conflowgen import PortCallManager
from conflowgen.application.models.container_flow_generation_properties import ContainerFlowGenerationProperties
from conflowgen.application.repositories.container_flow_generation_properties_repository import \
    ContainerFlowGenerationPropertiesRepository
from conflowgen.database_connection.create_tables import create_tables
from conflowgen.domain_models.distribution_models.container_dwell_time_distribution import \
    ContainerDwellTimeDistribution
from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.distribution_models.storage_requirement_distribution import StorageRequirementDistribution
from conflowgen.domain_models.distribution_seeders import mode_of_transport_distribution_seeder, \
    seed_all_distributions, container_dwell_time_distribution_seeder
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
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
            ContainerDwellTimeDistribution
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
        port_call_manager.add_large_scheduled_vehicle(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeeder",
            vehicle_arrives_at=datetime.date(2021, 7, 9),
            vehicle_arrives_at_time=datetime.time(11),
            average_vehicle_capacity=800,
            average_moved_capacity=100,
            next_destinations=None
        )
        port_call_manager.add_large_scheduled_vehicle(
            vehicle_type=ModeOfTransport.deep_sea_vessel,
            service_name="TestDeepSeaVessel",
            vehicle_arrives_at=datetime.date(2021, 7, 9),
            vehicle_arrives_at_time=datetime.time(11),
            average_vehicle_capacity=800,
            average_moved_capacity=100,
            next_destinations=None
        )
        self.container_flow_generator_service.generate()

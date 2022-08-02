import unittest

from conflowgen import ContainerLength, StorageRequirement
from conflowgen.domain_models.container import Container
from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.distribution_seeders import mode_of_transport_distribution_seeder
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.vehicle import LargeScheduledVehicle, Truck
from conflowgen.flow_generator.container_flow_generation_service import \
    ContainerFlowGenerationService
from conflowgen.domain_models.large_vehicle_schedule import Schedule, Destination
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestContainerFlowGeneratorService__generate(unittest.TestCase):  # pylint: disable=invalid-name

    def setUp(self) -> None:
        """Create container database in memory"""
        self.sqlite_db = setup_sqlite_in_memory_db()
        self.sqlite_db.create_tables([
            Container,
            ModeOfTransportDistribution,
            Schedule,
            Destination,
            Truck,
            LargeScheduledVehicle
        ])
        mode_of_transport_distribution_seeder.seed()
        self.container_flow_generator_service = ContainerFlowGenerationService()

    def test_container_flow_data_exists_with_no_data(self):
        container_flow_data_exists = self.container_flow_generator_service.container_flow_data_exists()
        self.assertFalse(container_flow_data_exists)

    def test_container_flow_data_exists_with_some_data(self):
        Container.create(
            weight=20,
            length=ContainerLength.twenty_feet,
            storage_requirement=StorageRequirement.standard,
            delivered_by=ModeOfTransport.feeder,
            picked_up_by=ModeOfTransport.truck,
            picked_up_by_initial=ModeOfTransport.truck
        )
        container_flow_data_exists = self.container_flow_generator_service.container_flow_data_exists()
        self.assertTrue(container_flow_data_exists)

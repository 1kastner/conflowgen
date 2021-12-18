import datetime
import unittest
import unittest.mock

from conflowgen import ContainerFlowGenerationManager
from conflowgen.application.models.container_flow_generation_properties import ContainerFlowGenerationProperties
from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.distribution_seeders import mode_of_transport_distribution_seeder
from conflowgen.domain_models.large_vehicle_schedule import Schedule
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestContainerFlowGenerationManager__set_properties(unittest.TestCase):

    def setUp(self) -> None:
        """Create container database in memory"""
        sqlite_db = setup_sqlite_in_memory_db()
        sqlite_db.create_tables([
            ContainerFlowGenerationProperties,
            ModeOfTransportDistribution,
            Schedule
        ])
        mode_of_transport_distribution_seeder.seed()
        self.container_flow_generation_manager = ContainerFlowGenerationManager()

    def test_set_properties(self):
        with unittest.mock.patch.object(
                self.container_flow_generation_manager.container_flow_generation_properties_repository,
                'set_container_flow_generation_properties',
                return_value=None) as mock_method:
            self.container_flow_generation_manager.set_properties(
                datetime.datetime.now().date(), datetime.datetime.now().date()
            )
        properties = ContainerFlowGenerationProperties.get()
        mock_method.assert_called_once_with(properties)

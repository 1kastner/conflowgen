import datetime
import unittest
import unittest.mock

from conflowgen.api.container_flow_generation_manager import ContainerFlowGenerationManager
from conflowgen.application.models.container_flow_generation_properties import ContainerFlowGenerationProperties
from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.distribution_seeders import mode_of_transport_distribution_seeder
from conflowgen.domain_models.large_vehicle_schedule import Schedule
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestContainerFlowGenerationManager(unittest.TestCase):

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

    def test_generate_with_overwrite(self):
        with unittest.mock.patch.object(
                self.container_flow_generation_manager.container_flow_generation_service,
                'generate',
                return_value=None) as mock_method:
            self.container_flow_generation_manager.generate(overwrite=True)
        mock_method.assert_called_once()

    def test_generate_without_overwrite_and_no_previous_data(self):
        with unittest.mock.patch.object(
                self.container_flow_generation_manager.container_flow_generation_service,
                'generate',
                return_value=None) as mock_generate, \
            unittest.mock.patch.object(
                self.container_flow_generation_manager.container_flow_generation_service,
                'container_flow_data_exists',
                return_value=False) as mock_check:
            self.container_flow_generation_manager.generate(overwrite=False)
        mock_check.assert_called_once()
        mock_generate.assert_called_once()

    def test_generate_without_overwrite_and_some_previous_data(self):
        with unittest.mock.patch.object(
                self.container_flow_generation_manager.container_flow_generation_service,
                'generate',
                return_value=None) as mock_generate, \
            unittest.mock.patch.object(
                self.container_flow_generation_manager.container_flow_generation_service,
                'container_flow_data_exists',
                return_value=True) as mock_check:
            self.container_flow_generation_manager.generate(overwrite=False)
        mock_check.assert_called_once()
        mock_generate.assert_not_called()

    def test_get_properties(self):

        class MockedProperties:
            name = "my test data"
            start_date = datetime.date(2030, 1, 1)
            end_date = datetime.date(2030, 12, 31)
            transportation_buffer = 0.2
            minimum_dwell_time_of_import_containers_in_hours = 3
            minimum_dwell_time_of_export_containers_in_hours = 4
            minimum_dwell_time_of_transshipment_containers_in_hours = 5
            maximum_dwell_time_of_import_containers_in_hours = 40
            maximum_dwell_time_of_export_containers_in_hours = 50
            maximum_dwell_time_of_transshipment_containers_in_hours = 60

        dict_properties = {
            'name': "my test data",
            'start_date': datetime.date(2030, 1, 1),
            'end_date': datetime.date(2030, 12, 31),
            'transportation_buffer': 0.2,
            'minimum_dwell_time_of_import_containers_in_hours': 3,
            'minimum_dwell_time_of_export_containers_in_hours': 4,
            'minimum_dwell_time_of_transshipment_containers_in_hours': 5,
            'maximum_dwell_time_of_import_containers_in_hours': 40,
            'maximum_dwell_time_of_export_containers_in_hours': 50,
            'maximum_dwell_time_of_transshipment_containers_in_hours': 60
        }

        with unittest.mock.patch.object(
                self.container_flow_generation_manager.container_flow_generation_properties_repository,
                'get_container_flow_generation_properties',
                return_value=MockedProperties) as mock_method:
            retrieved_properties = self.container_flow_generation_manager.get_properties()
        mock_method.assert_called_once()
        self.assertDictEqual(dict_properties, retrieved_properties)

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

    def test_container_flow_data_exists(self):
        with unittest.mock.patch.object(
                self.container_flow_generation_manager.container_flow_generation_service,
                'container_flow_data_exists',
                return_value=True) as mock_method:
            response = self.container_flow_generation_manager.container_flow_data_exists()
        mock_method.assert_called_once()
        self.assertTrue(response)

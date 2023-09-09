import unittest
import unittest.mock
import datetime

from conflowgen.api.container_dwell_time_distribution_manager import ContainerDwellTimeDistributionManager
from conflowgen.domain_models.distribution_models.container_dwell_time_distribution import \
    ContainerDwellTimeDistribution
from conflowgen.domain_models.distribution_models.storage_requirement_distribution import StorageRequirementDistribution
from conflowgen.domain_models.distribution_seeders import container_dwell_time_distribution_seeder
from conflowgen.domain_models.distribution_seeders import storage_requirement_distribution_seeder

from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.api.container_length_distribution_manager import ContainerLengthDistributionManager
from conflowgen.domain_models.distribution_models.container_length_distribution import ContainerLengthDistribution
from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.distribution_repositories.mode_of_transport_distribution_repository import \
    ModeOfTransportDistributionRepository
from conflowgen.domain_models.large_vehicle_schedule import Schedule
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestContainerDwellTimeDistributionManager(unittest.TestCase):

    SAMPLE_DISTRIBUTION = container_dwell_time_distribution_seeder.DEFAULT_CONTAINER_DWELL_TIME_DISTRIBUTIONS

    def setUp(self) -> None:
        self.sqlite_db = setup_sqlite_in_memory_db()
        self.sqlite_db.create_tables([
            Schedule,
            ModeOfTransportDistribution,
            ContainerDwellTimeDistribution,
            ContainerLengthDistribution,
            StorageRequirementDistribution
        ])

        self.container_dwell_time_distribution_manager = ContainerDwellTimeDistributionManager()

        ModeOfTransportDistributionRepository().set_mode_of_transport_distributions({
            ModeOfTransport.truck: {
                ModeOfTransport.truck: 0,
                ModeOfTransport.train: 0,
                ModeOfTransport.barge: 0,
                ModeOfTransport.feeder: 0.5,
                ModeOfTransport.deep_sea_vessel: 0.5
            },
            ModeOfTransport.train: {
                ModeOfTransport.truck: 0,
                ModeOfTransport.train: 0,
                ModeOfTransport.barge: 0,
                ModeOfTransport.feeder: 0.5,
                ModeOfTransport.deep_sea_vessel: 0.5
            },
            ModeOfTransport.barge: {
                ModeOfTransport.truck: 0,
                ModeOfTransport.train: 0,
                ModeOfTransport.barge: 0,
                ModeOfTransport.feeder: 0.5,
                ModeOfTransport.deep_sea_vessel: 0.5
            },
            ModeOfTransport.feeder: {
                ModeOfTransport.truck: 0.2,
                ModeOfTransport.train: 0.4,
                ModeOfTransport.barge: 0.1,
                ModeOfTransport.feeder: 0.15,
                ModeOfTransport.deep_sea_vessel: 0.15
            },
            ModeOfTransport.deep_sea_vessel: {
                ModeOfTransport.truck: 0.2,
                ModeOfTransport.train: 0.4,
                ModeOfTransport.barge: 0.1,
                ModeOfTransport.feeder: 0.15,
                ModeOfTransport.deep_sea_vessel: 0.15
            }
        })

        container_length_manager = ContainerLengthDistributionManager()
        container_length_manager.set_container_length_distribution(  # Set default container length distribution
            {
                ContainerLength.other: 0.001,
                ContainerLength.twenty_feet: 0.4,
                ContainerLength.forty_feet: 0.57,
                ContainerLength.forty_five_feet: 0.029
            }
        )

        container_dwell_time_distribution_manager = ContainerDwellTimeDistributionManager()
        container_dwell_time_distribution_manager.set_container_dwell_time_distribution(self.SAMPLE_DISTRIBUTION)

        storage_requirement_distribution_seeder.seed()

    def test_get_container_dwell_time_distributions(self):
        with unittest.mock.patch.object(
                self.container_dwell_time_distribution_manager.container_dwell_time_distribution_repository,
                'get_distributions',
                return_value=self.SAMPLE_DISTRIBUTION) as mock_method:
            distribution = self.container_dwell_time_distribution_manager.get_container_dwell_time_distribution()
        mock_method.assert_called_once()
        self.assertEqual(distribution, self.SAMPLE_DISTRIBUTION)

    def test_set_container_dwell_time_distributions(self):
        with unittest.mock.patch.object(
                self.container_dwell_time_distribution_manager.container_dwell_time_distribution_repository,
                'set_distributions',
                return_value=None) as mock_method:
            self.container_dwell_time_distribution_manager.set_container_dwell_time_distribution(
                self.SAMPLE_DISTRIBUTION
            )
        mock_method.assert_called_once_with(self.SAMPLE_DISTRIBUTION)

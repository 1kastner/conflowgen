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

    def test_get_average_container_dwell_time_base_case(self):
        one_week_later = datetime.datetime.now() + datetime.timedelta(weeks=1)
        schedule = Schedule.create(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeederService",
            vehicle_arrives_at=one_week_later.date(),
            vehicle_arrives_at_time=one_week_later.time(),
            average_vehicle_capacity=300,
            average_moved_capacity=300,
            vehicle_arrives_every_k_days=-1
        )
        schedule.save()

        now = datetime.datetime.now()
        average_container_dwell_time = self.container_dwell_time_distribution_manager.get_average_container_dwell_time(
            start_date=now.date(),
            end_date=(now + datetime.timedelta(weeks=2)).date(),
        )

        print("average_container_dwell_time: ", average_container_dwell_time)
        self.assertEqual(average_container_dwell_time, 129.9408)

    def test_get_average_container_dwell_time_1_sd(self):
        one_week_later = datetime.datetime.now() + datetime.timedelta(weeks=1)
        schedule = Schedule.create(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeederService",
            vehicle_arrives_at=one_week_later.date(),
            vehicle_arrives_at_time=one_week_later.time(),
            average_vehicle_capacity=300,
            average_moved_capacity=300,
            vehicle_arrives_every_k_days=-1
        )
        schedule.save()

        # Container dwell time increase
        container_dwell_time_increase = 1

        container_dwell_time_distribution_manager = ContainerDwellTimeDistributionManager()

        original_dwell_time_distributions = container_dwell_time_distribution_manager.\
            get_container_dwell_time_distribution()

        new_container_dwell_time_distributions = {}

        for mode1, mode1_dict in original_dwell_time_distributions.items():
            new_mode1_dict = {}
            for mode2, mode2_dict in mode1_dict.items():
                new_mode2_dict = {}
                for requirement, distribution in mode2_dict.items():
                    sd = distribution.variance ** 0.5
                    new_average = distribution.average + sd * container_dwell_time_increase
                    new_maximum = new_average * 3  # Necessary to avoid average > max
                    # Create a new dictionary with updated average value
                    new_distribution_dict = {
                        "distribution_name": "lognormal",
                        "average_number_of_hours": new_average,
                        "variance": distribution.variance,  # Keep variance same
                        "minimum_number_of_hours": distribution.minimum,  # Keep minimum same
                        "maximum_number_of_hours": new_maximum,
                    }
                    new_mode2_dict[requirement] = new_distribution_dict
                new_mode1_dict[mode2] = new_mode2_dict
            new_container_dwell_time_distributions[mode1] = new_mode1_dict

        container_dwell_time_distribution_manager.set_container_dwell_time_distribution(
            new_container_dwell_time_distributions)

        now = datetime.datetime.now()
        average_container_dwell_time = self.container_dwell_time_distribution_manager.get_average_container_dwell_time(
            start_date=now.date(),
            end_date=(now + datetime.timedelta(weeks=2)).date(),
        )

        print("average_container_dwell_time: ", average_container_dwell_time)
        self.assertEqual(average_container_dwell_time, 207.68489589654993)

    def test_get_average_container_dwell_time_2_sd(self):
        one_week_later = datetime.datetime.now() + datetime.timedelta(weeks=1)
        schedule = Schedule.create(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeederService",
            vehicle_arrives_at=one_week_later.date(),
            vehicle_arrives_at_time=one_week_later.time(),
            average_vehicle_capacity=300,
            average_moved_capacity=300,
            vehicle_arrives_every_k_days=-1
        )
        schedule.save()

        # Container dwell time increase
        container_dwell_time_increase = 2

        container_dwell_time_distribution_manager = ContainerDwellTimeDistributionManager()

        original_dwell_time_distributions = container_dwell_time_distribution_manager.\
            get_container_dwell_time_distribution()

        new_container_dwell_time_distributions = {}

        for mode1, mode1_dict in original_dwell_time_distributions.items():
            new_mode1_dict = {}
            for mode2, mode2_dict in mode1_dict.items():
                new_mode2_dict = {}
                for requirement, distribution in mode2_dict.items():
                    sd = distribution.variance ** 0.5
                    new_average = distribution.average + sd * container_dwell_time_increase
                    new_maximum = new_average * 3  # Necessary to avoid average > max
                    # Create a new dictionary with updated average value
                    new_distribution_dict = {
                        "distribution_name": "lognormal",
                        "average_number_of_hours": new_average,
                        "variance": distribution.variance,  # Keep variance same
                        "minimum_number_of_hours": distribution.minimum,  # Keep minimum same
                        "maximum_number_of_hours": new_maximum,
                    }
                    new_mode2_dict[requirement] = new_distribution_dict
                new_mode1_dict[mode2] = new_mode2_dict
            new_container_dwell_time_distributions[mode1] = new_mode1_dict

        container_dwell_time_distribution_manager.set_container_dwell_time_distribution(
            new_container_dwell_time_distributions)

        now = datetime.datetime.now()
        average_container_dwell_time = self.container_dwell_time_distribution_manager.get_average_container_dwell_time(
            start_date=now.date(),
            end_date=(now + datetime.timedelta(weeks=2)).date(),
        )

        self.assertEqual(average_container_dwell_time, 285.42899179309984)

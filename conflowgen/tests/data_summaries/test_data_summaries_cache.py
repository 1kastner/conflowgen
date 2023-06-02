import unittest
import datetime

from conflowgen import ContainerLength, TruckArrivalDistributionManager, ModeOfTransport, TruckGateThroughputPreview
from conflowgen.application.models.container_flow_generation_properties import ContainerFlowGenerationProperties
from conflowgen.data_summaries import DataSummariesCache
from conflowgen.domain_models.distribution_models.container_length_distribution import ContainerLengthDistribution
from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.distribution_models.truck_arrival_distribution import TruckArrivalDistribution
from conflowgen.domain_models.distribution_repositories.container_length_distribution_repository import \
    ContainerLengthDistributionRepository
from conflowgen.domain_models.distribution_repositories.mode_of_transport_distribution_repository import \
    ModeOfTransportDistributionRepository
from conflowgen.domain_models.large_vehicle_schedule import Schedule
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestDataSummariesCache(unittest.TestCase):

    def setUp(self) -> None:
        """Create container database in memory"""
        self.sqlite_db = setup_sqlite_in_memory_db()
        self.sqlite_db.create_tables([
            Schedule,
            ModeOfTransportDistribution,
            ContainerLengthDistribution,
            ContainerFlowGenerationProperties,
            TruckArrivalDistribution
        ])
        now = datetime.datetime.now()
        ModeOfTransportDistributionRepository().set_mode_of_transport_distributions({
            ModeOfTransport.truck: {
                ModeOfTransport.truck: 0.1,
                ModeOfTransport.train: 0,
                ModeOfTransport.barge: 0,
                ModeOfTransport.feeder: 0.4,
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
        ContainerLengthDistributionRepository().set_distribution({
            ContainerLength.twenty_feet: 1,
            ContainerLength.forty_feet: 0,
            ContainerLength.forty_five_feet: 0,
            ContainerLength.other: 0
        })
        ContainerFlowGenerationProperties.create(
            start_date=now,
            end_date=now + datetime.timedelta(weeks=2)
        )  # mostly use default values
        arrival_distribution = {
            3: .2,
            4: .8
        }
        truck_arrival_distribution_manager = TruckArrivalDistributionManager()
        truck_arrival_distribution_manager.set_truck_arrival_distribution(arrival_distribution)
        self.preview = TruckGateThroughputPreview(
            start_date=now.date(),
            end_date=(now + datetime.timedelta(weeks=2)).date(),
            transportation_buffer=0.0
        )

    def sanity_test(self):
        # Define a function to be decorated
        @DataSummariesCache.cache_result
        def my_function(n):
            return n ** 2

        # Clear the cache before running the test
        DataSummariesCache.reset_cache()

        # Test case 1: Call the decorated function with argument 5
        result = my_function(5)
        assert result == 25, "Test case 1 failed"

        # Test case 2: Call the decorated function with argument 5 again
        # This should retrieve the cached result from the previous call
        result = my_function(5)
        assert result == 25, "Test case 2 failed"

        # Test case 3: Call the decorated function with argument 10
        result = my_function(10)
        assert result == 100, "Test case 3 failed"

    def test_with_preview(self):
        cache = DataSummariesCache()  # This is technically incorrect usage of the cache as it should never be
        # instantiated, but it's the easiest way to test it

        two_days_later = datetime.datetime.now() + datetime.timedelta(days=2)
        Schedule.create(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeederService",
            vehicle_arrives_at=two_days_later.date(),
            vehicle_arrives_every_k_days=-1,
            vehicle_arrives_at_time=two_days_later.time(),
            average_vehicle_capacity=300,
            average_moved_capacity=300
        )
        self.preview.get_weekly_truck_arrivals(True, True)
        self.preview.get_weekly_truck_arrivals(True, True)

        # pylint: disable=protected-access
        self.assertEqual(len(cache.cached_results), 7)
        # Cannot compare the entries themselves, because the keys are based on IDs of the functions, which are reset
        # every time program is run

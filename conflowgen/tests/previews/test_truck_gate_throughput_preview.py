import unittest
import datetime

from conflowgen import ModeOfTransport, ContainerLength, TruckArrivalDistributionManager
from conflowgen.application.models.container_flow_generation_properties import ContainerFlowGenerationProperties
from conflowgen.domain_models.distribution_models.container_length_distribution import ContainerLengthDistribution
from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.distribution_models.truck_arrival_distribution import TruckArrivalDistribution
from conflowgen.domain_models.distribution_repositories.container_length_distribution_repository import \
    ContainerLengthDistributionRepository
from conflowgen.domain_models.distribution_repositories.mode_of_transport_distribution_repository import \
    ModeOfTransportDistributionRepository
from conflowgen.domain_models.large_vehicle_schedule import Schedule
from conflowgen.previews.truck_gate_throughput_preview import TruckGateThroughputPreview
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestTruckGateThroughputPreview(unittest.TestCase):

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

    def test_get_total_trucks(self):
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
        # pylint: disable=protected-access
        total_trucks = self.preview._get_total_trucks()
        # 300 TEU arrive by feeder
        # 300 TEU * 0.2 (from mode of transport distribution) = 60 TEU to be exported by truck
        # Only twenty-feet containers used, so 60 TEU = 60 trucks needed
        self.assertEqual(total_trucks, (60, 60))

    def test_get_weekly_trucks(self):
        # pylint: disable=protected-access
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
        weekly_trucks = self.preview._get_number_of_trucks_per_week()
        # 60 trucks total (from test_get_total_trucks above)
        # 60 trucks / 2 weeks = 30 trucks per week
        self.assertEqual(weekly_trucks, (30, 30))

    def test_get_truck_distribution(self):
        # Test case 1
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
        weekly_truck_distribution = self.preview.get_weekly_truck_arrivals(True, False)
        self.assertEqual(weekly_truck_distribution, {3: 6, 4: 24})
        weekly_truck_distribution = self.preview.get_weekly_truck_arrivals(True, True)
        self.assertEqual(weekly_truck_distribution, {3: 12, 4: 48})
        weekly_truck_distribution = self.preview.get_weekly_truck_arrivals(False, True)
        self.assertEqual(weekly_truck_distribution, {3: 6, 4: 24})

    def test_with_no_outbound_truck_traffic(self):
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
                ModeOfTransport.truck: 0,
                ModeOfTransport.train: 0.6,
                ModeOfTransport.barge: 0.1,
                ModeOfTransport.feeder: 0.15,
                ModeOfTransport.deep_sea_vessel: 0.15
            },
            ModeOfTransport.deep_sea_vessel: {
                ModeOfTransport.truck: 0,
                ModeOfTransport.train: 0.6,
                ModeOfTransport.barge: 0.1,
                ModeOfTransport.feeder: 0.15,
                ModeOfTransport.deep_sea_vessel: 0.15
            }
        })
        weekly_truck_distribution = self.preview.get_weekly_truck_arrivals(False, True)
        self.assertEqual(weekly_truck_distribution, {3: 0, 4: 0})

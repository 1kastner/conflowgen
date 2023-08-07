import datetime
import unittest

from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.api.container_length_distribution_manager import ContainerLengthDistributionManager
from conflowgen.application.models.container_flow_generation_properties import ContainerFlowGenerationProperties
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.distribution_models.container_length_distribution import ContainerLengthDistribution
from conflowgen.domain_models.distribution_repositories.mode_of_transport_distribution_repository import \
    ModeOfTransportDistributionRepository
from conflowgen.domain_models.large_vehicle_schedule import Schedule
from conflowgen.previews.container_flow_by_vehicle_type_preview_report import \
    ContainerFlowByVehicleTypePreviewReport
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestContainerFlowByVehicleTypePreviewReport(unittest.TestCase):
    def setUp(self) -> None:
        """Create container database in memory"""
        self.sqlite_db = setup_sqlite_in_memory_db()
        self.sqlite_db.create_tables([
            Schedule,
            ModeOfTransportDistribution,
            ContainerFlowGenerationProperties,
            ContainerLengthDistribution
        ])
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

        now = datetime.datetime.now()
        ContainerFlowGenerationProperties.create(
            start_date=now,
            end_date=now + datetime.timedelta(weeks=2)
        ).save()  # mostly use default values
        self.preview_report = ContainerFlowByVehicleTypePreviewReport()
        self.preview_report.reload()

    def test_report_with_no_schedules(self):
        """If no schedules are provided, no flows exist"""
        actual_report = self.preview_report.get_report_as_text()
        expected_report = """
vehicle type (from) vehicle type (to) required capacity (in TEU)
deep sea vessel     deep sea vessel                          0.0
deep sea vessel     feeder                                   0.0
deep sea vessel     barge                                    0.0
deep sea vessel     train                                    0.0
deep sea vessel     truck                                    0.0
feeder              deep sea vessel                          0.0
feeder              feeder                                   0.0
feeder              barge                                    0.0
feeder              train                                    0.0
feeder              truck                                    0.0
barge               deep sea vessel                          0.0
barge               feeder                                   0.0
barge               barge                                    0.0
barge               train                                    0.0
barge               truck                                    0.0
train               deep sea vessel                          0.0
train               feeder                                   0.0
train               barge                                    0.0
train               train                                    0.0
train               truck                                    0.0
truck               deep sea vessel                          0.0
truck               feeder                                   0.0
truck               barge                                    0.0
truck               train                                    0.0
truck               truck                                    0.0
(rounding errors might exist)
"""
        self.assertEqual(expected_report, actual_report)

    def test_inbound_with_single_arrival_schedules(self):
        one_week_later = datetime.datetime.now() + datetime.timedelta(weeks=1)
        Schedule.create(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeederService",
            vehicle_arrives_at=one_week_later.date(),
            vehicle_arrives_at_time=one_week_later.time(),
            average_vehicle_capacity=400,
            average_moved_capacity=300,
            vehicle_arrives_every_k_days=-1
        )
        actual_report = self.preview_report.get_report_as_text()
        expected_report = """
vehicle type (from) vehicle type (to) required capacity (in TEU)
deep sea vessel     deep sea vessel                          0.0
deep sea vessel     feeder                                   0.0
deep sea vessel     barge                                    0.0
deep sea vessel     train                                    0.0
deep sea vessel     truck                                    0.0
feeder              deep sea vessel                         45.0
feeder              feeder                                  45.0
feeder              barge                                   30.0
feeder              train                                  120.0
feeder              truck                                   60.0
barge               deep sea vessel                          0.0
barge               feeder                                   0.0
barge               barge                                    0.0
barge               train                                    0.0
barge               truck                                    0.0
train               deep sea vessel                          0.0
train               feeder                                   0.0
train               barge                                    0.0
train               train                                    0.0
train               truck                                    0.0
truck               deep sea vessel                         30.0
truck               feeder                                  30.0
truck               barge                                    0.0
truck               train                                    0.0
truck               truck                                    0.0
(rounding errors might exist)
"""
        self.assertEqual(expected_report, actual_report)

    def test_report_with_no_schedules_as_graph(self):
        """Not throwing an exception is sufficient"""
        fig = self.preview_report.get_report_as_graph()
        self.assertIsNotNone(fig)

    def test_report_with_schedules_as_graph(self):
        """Not throwing an exception is sufficient for now"""
        one_week_later = datetime.datetime.now() + datetime.timedelta(weeks=1)
        Schedule.create(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeederService",
            vehicle_arrives_at=one_week_later.date(),
            vehicle_arrives_at_time=one_week_later.time(),
            average_vehicle_capacity=400,
            average_moved_capacity=300,
            vehicle_arrives_every_k_days=-1
        )
        fig = self.preview_report.get_report_as_graph()
        self.assertIsNotNone(fig)

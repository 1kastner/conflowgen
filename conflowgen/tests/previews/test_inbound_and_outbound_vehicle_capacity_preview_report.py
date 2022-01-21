import datetime
import unittest

from conflowgen.application.models.container_flow_generation_properties import ContainerFlowGenerationProperties
from conflowgen.domain_models.distribution_repositories.mode_of_transport_distribution_repository import \
    ModeOfTransportDistributionRepository
from conflowgen.previews.inbound_and_outbound_vehicle_capacity_preview_report import \
    InboundAndOutboundVehicleCapacityPreviewReport
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.large_vehicle_schedule import Schedule
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestInboundAndOutboundVehicleCapacityPreviewReport(unittest.TestCase):
    def setUp(self) -> None:
        """Create container database in memory"""
        self.sqlite_db = setup_sqlite_in_memory_db()
        self.sqlite_db.create_tables([
            Schedule,
            ModeOfTransportDistribution,
            ContainerFlowGenerationProperties
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
        now = datetime.datetime.now()
        ContainerFlowGenerationProperties.create(
            start_date=now,
            end_date=now + datetime.timedelta(weeks=2)
        ).save()  # mostly use default values
        self.preview_report = InboundAndOutboundVehicleCapacityPreviewReport()
        self.preview_report.reload()

    def test_report_with_no_schedules(self):
        """If no schedules are provided, no capacity is needed"""
        actual_report = self.preview_report.get_report_as_text()
        expected_report = """
vehicle type    inbound capacity (in TEU) outbound avg capacity (in TEU) outbound max capacity (in TEU)
deep sea vessel                       0.0                            0.0                            0.0
feeder                                0.0                            0.0                            0.0
barge                                 0.0                            0.0                            0.0
train                                 0.0                            0.0                            0.0
truck                                 0.0                            0.0                           -1.0
(rounding errors might exist)
"""
        self.assertEqual(expected_report, actual_report)

    def test_inbound_with_single_arrival_schedules(self):
        one_week_later = datetime.datetime.now() + datetime.timedelta(weeks=1)
        schedule = Schedule.create(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeederService",
            vehicle_arrives_at=one_week_later.date(),
            vehicle_arrives_at_time=one_week_later.time(),
            average_vehicle_capacity=400,
            average_moved_capacity=300,
            vehicle_arrives_every_k_days=-1
        )
        schedule.save()
        actual_report = self.preview_report.get_report_as_text()
        expected_report = """
vehicle type    inbound capacity (in TEU) outbound avg capacity (in TEU) outbound max capacity (in TEU)
deep sea vessel                       0.0                            0.0                            0.0
feeder                              300.0                          300.0                          360.0
barge                                 0.0                            0.0                            0.0
train                                 0.0                            0.0                            0.0
truck                                60.0                           60.0                           -1.0
(rounding errors might exist)
"""
        self.assertEqual(expected_report, actual_report)

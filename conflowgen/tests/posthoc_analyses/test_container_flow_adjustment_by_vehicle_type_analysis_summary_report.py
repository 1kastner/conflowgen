import datetime
import unittest

from conflowgen.application.models.container_flow_generation_properties import ContainerFlowGenerationProperties
from conflowgen.domain_models.container import Container
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.distribution_seeders import mode_of_transport_distribution_seeder
from conflowgen.domain_models.large_vehicle_schedule import Schedule, Destination
from conflowgen.domain_models.vehicle import LargeScheduledVehicle, Truck, Feeder
from conflowgen.posthoc_analyses.container_flow_adjustment_by_vehicle_type_analysis_summary_report import \
    ContainerFlowAdjustmentByVehicleTypeAnalysisSummaryReport
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestContainerFlowAdjustmentByVehicleTypeAnalysisReport(unittest.TestCase):
    def setUp(self) -> None:
        """Create container database in memory"""
        self.sqlite_db = setup_sqlite_in_memory_db()
        self.sqlite_db.create_tables([
            Schedule,
            Container,
            LargeScheduledVehicle,
            Truck,
            Feeder,
            ModeOfTransportDistribution,
            Destination,
            ContainerFlowGenerationProperties
        ])
        mode_of_transport_distribution_seeder.seed()
        ContainerFlowGenerationProperties.create(
            start_date=datetime.datetime(2021, 12, 1),
            end_date=datetime.datetime(2021, 12, 6)
        )
        self.report = ContainerFlowAdjustmentByVehicleTypeAnalysisSummaryReport()

    def test_with_no_data(self):
        """If no schedules are provided, no capacity is needed"""
        actual_report = self.report.get_report_as_text()
        expected_report = """
                             Capacity in TEU
vehicle type unchanged:      0.0        (-%)
changed to deep sea vessel:  0.0        (-%)
changed to feeder:           0.0        (-%)
changed to barge:            0.0        (-%)
changed to train:            0.0        (-%)
changed to truck:            0.0        (-%)
(rounding errors might exist)
"""
        self.assertEqual(actual_report, expected_report)

    def test_with_two_containers(self):
        Container.create(
            weight=20,
            length=ContainerLength.twenty_feet,
            storage_requirement=StorageRequirement.standard,
            delivered_by=ModeOfTransport.feeder,
            delivered_by_large_scheduled_vehicle=None,
            picked_up_by=ModeOfTransport.truck,
            picked_up_by_initial=ModeOfTransport.truck
        )
        Container.create(
            weight=20,
            length=ContainerLength.forty_feet,
            storage_requirement=StorageRequirement.standard,
            delivered_by=ModeOfTransport.feeder,
            delivered_by_large_scheduled_vehicle=None,
            picked_up_by=ModeOfTransport.truck,
            picked_up_by_initial=ModeOfTransport.feeder
        )
        actual_report = self.report.get_report_as_text()
        expected_report = """
                             Capacity in TEU
vehicle type unchanged:      1.0        (33.33%)
changed to deep sea vessel:  0.0        (0.00%)
changed to feeder:           0.0        (0.00%)
changed to barge:            0.0        (0.00%)
changed to train:            0.0        (0.00%)
changed to truck:            2.0        (66.67%)
(rounding errors might exist)
"""
        self.assertEqual(actual_report, expected_report)

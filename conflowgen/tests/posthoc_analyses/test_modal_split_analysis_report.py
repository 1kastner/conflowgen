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
from conflowgen.posthoc_analyses.modal_split_analysis_report import ModalSplitAnalysisReport
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestModalSplitAnalysisReport(unittest.TestCase):
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
        ContainerFlowGenerationProperties.create()
        self.analysis = ModalSplitAnalysisReport()

    def test_with_no_data(self):
        actual_report = self.analysis.get_report_as_text()
        expected_report = """
Transshipment share
transshipment proportion (in TEU):       0.00 (-%)
hinterland proportion (in TEU):          0.00 (-%)

Inbound modal split
truck proportion (in TEU):        0.0 (-%)
barge proportion (in TEU):        0.0 (-%)
train proportion (in TEU):        0.0 (-%)

Outbound modal split
truck proportion (in TEU):        0.0 (-%)
barge proportion (in TEU):        0.0 (-%)
train proportion (in TEU):        0.0 (-%)

Absolute modal split (both inbound and outbound)
truck proportion (in TEU):        0.0 (-%)
barge proportion (in TEU):        0.0 (-%)
train proportion (in TEU):        0.0 (-%)
(rounding errors might exist)
"""
        self.assertEqual(actual_report, expected_report)

    def test_inbound_with_single_feeder(self):
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
        feeder_lsv = LargeScheduledVehicle.create(
            capacity_in_teu=300,
            moved_capacity=schedule.average_moved_capacity,
            scheduled_arrival=datetime.datetime.now(),
            schedule=schedule
        )
        feeder_lsv.save()
        feeder = Feeder.create(
            large_scheduled_vehicle=feeder_lsv
        )
        feeder.save()
        container = Container.create(
            weight=20,
            length=ContainerLength.twenty_feet,
            storage_requirement=StorageRequirement.standard,
            delivered_by=ModeOfTransport.feeder,
            delivered_by_large_scheduled_vehicle=feeder_lsv,
            picked_up_by=ModeOfTransport.truck,
            picked_up_by_initial=ModeOfTransport.truck
        )
        container.save()

        actual_report = self.analysis.get_report_as_text()
        expected_report = """
Transshipment share
transshipment proportion (in TEU):       0.00 (0.00%)
hinterland proportion (in TEU):          1.00 (100.00%)

Inbound modal split
truck proportion (in TEU):        0.0 (-%)
barge proportion (in TEU):        0.0 (-%)
train proportion (in TEU):        0.0 (-%)

Outbound modal split
truck proportion (in TEU):        1.0 (100.00%)
barge proportion (in TEU):        0.0 (0.00%)
train proportion (in TEU):        0.0 (0.00%)

Absolute modal split (both inbound and outbound)
truck proportion (in TEU):        1.0 (100.00%)
barge proportion (in TEU):        0.0 (0.00%)
train proportion (in TEU):        0.0 (0.00%)
(rounding errors might exist)
"""
        self.assertEqual(actual_report, expected_report)

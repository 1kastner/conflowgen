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
from conflowgen.posthoc_analyses.inbound_to_outbound_vehicle_capacity_utilization_analysis_report import \
    InboundToOutboundVehicleCapacityUtilizationAnalysisReport
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestInboundToOutboundCapacityUtilizationAnalysisReport(unittest.TestCase):
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
            start_date=datetime.date(2021, 12, 15),
            end_date=datetime.date(2021, 12, 17)
        )
        self.analysis = InboundToOutboundVehicleCapacityUtilizationAnalysisReport()

    def test_with_no_data(self):
        actual_report = self.analysis.get_report_as_text()
        print(actual_report)
        expected_report = """
vehicle identifier                                 inbound capacity (in TEU) outbound capacity (in TEU)
--no vehicles exist--
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
            average_moved_capacity=250,
            vehicle_arrives_every_k_days=-1
        )
        schedule.save()
        feeder_lsv = LargeScheduledVehicle.create(
            vehicle_name="TestFeeder1",
            capacity_in_teu=schedule.average_vehicle_capacity,
            moved_capacity=schedule.average_moved_capacity,
            scheduled_arrival=datetime.datetime.now(),
            schedule=schedule
        )
        feeder_lsv.save()
        feeder = Feeder.create(
            large_scheduled_vehicle=feeder_lsv
        )
        feeder.save()
        Container.create(
            weight=20,
            length=ContainerLength.twenty_feet,
            storage_requirement=StorageRequirement.standard,
            delivered_by=ModeOfTransport.truck,
            picked_up_by_large_scheduled_vehicle=feeder_lsv,
            picked_up_by=ModeOfTransport.feeder,
            picked_up_by_initial=ModeOfTransport.truck
        )

        actual_report = self.analysis.get_report_as_text()
        print(actual_report)
        expected_report = """
vehicle identifier                                 inbound capacity (in TEU) outbound capacity (in TEU)
feeder-TestFeederService-TestFeeder1                                   250.0                        1.0
(rounding errors might exist)
"""
        self.assertEqual(actual_report, expected_report)

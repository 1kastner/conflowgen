import datetime

from conflowgen.analyses.outbound_to_inbound_vehicle_capacity_utilization_analysis_report import \
    OutboundToInboundVehicleCapacityUtilizationAnalysisReport
from conflowgen.application.models.container_flow_generation_properties import ContainerFlowGenerationProperties
from conflowgen.domain_models.container import Container
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.distribution_seeders import mode_of_transport_distribution_seeder
from conflowgen.domain_models.large_vehicle_schedule import Schedule, Destination
from conflowgen.domain_models.vehicle import LargeScheduledVehicle, Truck, Feeder
from conflowgen.tests.autoclose_matplotlib import UnitTestCaseWithMatplotlib
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


def setup_feeder_data():
    one_week_later = datetime.datetime.now() + datetime.timedelta(weeks=1)
    schedule = Schedule.create(
        vehicle_type=ModeOfTransport.feeder,
        service_name="TestFeederService",
        vehicle_arrives_at=one_week_later.date(),
        vehicle_arrives_at_time=one_week_later.time(),
        average_vehicle_capacity=300,
        average_inbound_container_volume=250,
        vehicle_arrives_every_k_days=-1
    )
    feeder_lsv = LargeScheduledVehicle.create(
        vehicle_name="TestFeeder1",
        capacity_in_teu=schedule.average_vehicle_capacity,
        inbound_container_volume=schedule.average_inbound_container_volume,
        scheduled_arrival=datetime.datetime.now(),
        schedule=schedule
    )
    Feeder.create(
        large_scheduled_vehicle=feeder_lsv
    )
    Container.create(
        weight=20,
        length=ContainerLength.twenty_feet,
        storage_requirement=StorageRequirement.standard,
        delivered_by=ModeOfTransport.truck,
        picked_up_by_large_scheduled_vehicle=feeder_lsv,
        picked_up_by=ModeOfTransport.feeder,
        picked_up_by_initial=ModeOfTransport.truck
    )


class TestInboundToOutboundCapacityUtilizationAnalysisReport(UnitTestCaseWithMatplotlib):
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
        self.report = OutboundToInboundVehicleCapacityUtilizationAnalysisReport()

    def test_with_no_data(self):
        actual_report = self.report.get_report_as_text()
        expected_report = """
vehicle type = scheduled vehicles
start date = none
end date = none
vehicle identifier                                 inbound volume (in TEU) outbound volume (in TEU)
--no vehicles exist--
"""
        self.assertEqual(actual_report, expected_report)

    def test_with_no_data_and_start_and_end_date(self):
        now = datetime.datetime(2022, 9, 17, 17, 58, 11)
        later = now + datetime.timedelta(hours=3)
        actual_report = self.report.get_report_as_text(
            start_date=now,
            end_date=later
        )
        expected_report = """
vehicle type = scheduled vehicles
start date = 2022-09-17T17:58:00
end date = 2022-09-17T20:58:00
vehicle identifier                                 inbound volume (in TEU) outbound volume (in TEU)
--no vehicles exist--
"""
        self.assertEqual(actual_report, expected_report)

    def test_inbound_with_single_feeder(self):
        setup_feeder_data()
        actual_report = self.report.get_report_as_text()
        expected_report = """
vehicle type = scheduled vehicles
start date = none
end date = none
vehicle identifier                                 inbound volume (in TEU) outbound volume (in TEU)
feeder-TestFeederService-TestFeeder1                                 250.0                      1.0
(rounding errors might exist)
"""
        self.assertEqual(actual_report, expected_report)

    def test_graph_with_feeder(self):
        setup_feeder_data()
        graph = self.report.get_report_as_graph()
        self.assertIsNotNone(graph)

    def test_graph_with_no_data(self):
        empty_graph = self.report.get_report_as_graph()
        self.assertIsNotNone(empty_graph)

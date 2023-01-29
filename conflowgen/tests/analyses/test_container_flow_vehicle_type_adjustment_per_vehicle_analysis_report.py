import datetime

from conflowgen.analyses.container_flow_vehicle_type_adjustment_per_vehicle_analysis_report import \
    ContainerFlowVehicleTypeAdjustmentPerVehicleAnalysisReport
from conflowgen.application.models.container_flow_generation_properties import ContainerFlowGenerationProperties
from conflowgen.domain_models.arrival_information import TruckArrivalInformationForDelivery, \
    TruckArrivalInformationForPickup
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
    when = datetime.datetime(2022, 9, 15, 13, 0)
    schedule = Schedule.create(
        vehicle_type=ModeOfTransport.feeder,
        service_name="TestFeederService",
        vehicle_arrives_at=when.date(),
        vehicle_arrives_at_time=when.time(),
        average_vehicle_capacity=300,
        average_moved_capacity=300,
        vehicle_arrives_every_k_days=-1
    )
    inbound_feeder_lsv = LargeScheduledVehicle.create(
        vehicle_name="TestFeeder1",
        capacity_in_teu=300,
        moved_capacity=schedule.average_moved_capacity,
        scheduled_arrival=datetime.datetime.now(),
        schedule=schedule
    )
    Feeder.create(
        large_scheduled_vehicle=inbound_feeder_lsv
    )
    vessel_arrival = datetime.datetime.now() + datetime.timedelta(days=3)
    outbound_feeder_lsv = LargeScheduledVehicle.create(
        vehicle_name="TestFeeder2",
        capacity_in_teu=300,
        moved_capacity=schedule.average_moved_capacity,
        scheduled_arrival=vessel_arrival,
        schedule=schedule
    )
    Container.create(
        weight=20,
        length=ContainerLength.twenty_feet,
        storage_requirement=StorageRequirement.standard,
        delivered_by=ModeOfTransport.feeder,
        delivered_by_large_scheduled_vehicle=inbound_feeder_lsv,
        picked_up_by=ModeOfTransport.feeder,
        picked_up_by_initial=ModeOfTransport.feeder,
        picked_up_by_large_scheduled_vehicle=outbound_feeder_lsv
    )


class TestContainerFlowVehicleTypeAdjustmentPerVehicleAnalysisReport(UnitTestCaseWithMatplotlib):
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
            ContainerFlowGenerationProperties,
            TruckArrivalInformationForPickup,
            TruckArrivalInformationForDelivery
        ])
        mode_of_transport_distribution_seeder.seed()
        ContainerFlowGenerationProperties.create(
            start_date=datetime.datetime(2021, 12, 1),
            end_date=datetime.datetime(2021, 12, 6)
        )
        self.analysis_report = ContainerFlowVehicleTypeAdjustmentPerVehicleAnalysisReport()

    def test_with_no_data(self):
        """If no schedules are provided, no capacity is needed"""
        actual_report = self.analysis_report.get_report_as_text()
        expected_report = """
initial vehicle type = scheduled vehicles
adjusted vehicle type = scheduled vehicles
start date = none
end date = none
vehicle identifier                                 fraction of adjusted containers (in containers)
--no vehicles exist--
"""
        self.assertEqual(actual_report, expected_report)

    def test_inbound_with_single_feeder(self):
        setup_feeder_data()
        actual_report = self.analysis_report.get_report_as_text()
        expected_report = """
initial vehicle type = scheduled vehicles
adjusted vehicle type = scheduled vehicles
start date = none
end date = none
vehicle identifier                                 fraction of adjusted containers (in containers)
feeder-TestFeederService-TestFeeder2               0.0%
(rounding errors might exist)
"""
        self.assertEqual(actual_report, expected_report)

    def test_graph(self):
        empty_graph = self.analysis_report.get_report_as_graph()
        self.assertIsNotNone(empty_graph)

    def test_graph_with_single_feeder(self):
        setup_feeder_data()
        graph = self.analysis_report.get_report_as_graph()
        self.assertIsNotNone(graph)

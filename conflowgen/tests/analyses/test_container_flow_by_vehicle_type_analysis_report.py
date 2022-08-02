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
from conflowgen.analyses.container_flow_by_vehicle_type_analysis_report import \
    ContainerFlowByVehicleTypeAnalysisReport
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


def setup_feeder_data():
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
        vehicle_name="TestFeeder1",
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


class TestContainerFlowByVehicleTypeAnalysisReport(unittest.TestCase):
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
        self.analysis = ContainerFlowByVehicleTypeAnalysisReport()

    def test_with_no_data(self):
        """If no schedules are provided, no capacity is needed"""
        actual_report = self.analysis.get_report_as_text()
        expected_report = """
vehicle type (from) vehicle type (to) transported capacity (in TEU)
deep sea vessel     deep sea vessel                             0.0
deep sea vessel     feeder                                      0.0
deep sea vessel     barge                                       0.0
deep sea vessel     train                                       0.0
deep sea vessel     truck                                       0.0
feeder              deep sea vessel                             0.0
feeder              feeder                                      0.0
feeder              barge                                       0.0
feeder              train                                       0.0
feeder              truck                                       0.0
barge               deep sea vessel                             0.0
barge               feeder                                      0.0
barge               barge                                       0.0
barge               train                                       0.0
barge               truck                                       0.0
train               deep sea vessel                             0.0
train               feeder                                      0.0
train               barge                                       0.0
train               train                                       0.0
train               truck                                       0.0
truck               deep sea vessel                             0.0
truck               feeder                                      0.0
truck               barge                                       0.0
truck               train                                       0.0
truck               truck                                       0.0
(rounding errors might exist)
"""
        self.assertEqual(actual_report, expected_report)

    def test_inbound_with_single_feeder(self):
        setup_feeder_data()
        actual_report = self.analysis.get_report_as_text()
        expected_report = """
vehicle type (from) vehicle type (to) transported capacity (in TEU)
deep sea vessel     deep sea vessel                             0.0
deep sea vessel     feeder                                      0.0
deep sea vessel     barge                                       0.0
deep sea vessel     train                                       0.0
deep sea vessel     truck                                       0.0
feeder              deep sea vessel                             0.0
feeder              feeder                                      0.0
feeder              barge                                       0.0
feeder              train                                       0.0
feeder              truck                                       1.0
barge               deep sea vessel                             0.0
barge               feeder                                      0.0
barge               barge                                       0.0
barge               train                                       0.0
barge               truck                                       0.0
train               deep sea vessel                             0.0
train               feeder                                      0.0
train               barge                                       0.0
train               train                                       0.0
train               truck                                       0.0
truck               deep sea vessel                             0.0
truck               feeder                                      0.0
truck               barge                                       0.0
truck               train                                       0.0
truck               truck                                       0.0
(rounding errors might exist)
"""
        self.assertEqual(actual_report, expected_report)

    def test_graph(self):
        empty_graph = self.analysis.get_report_as_graph()
        self.assertIsNotNone(empty_graph)

    def test_graph_with_single_feeder(self):
        setup_feeder_data()
        graph = self.analysis.get_report_as_graph()
        self.assertIsNotNone(graph)

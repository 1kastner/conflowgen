import datetime

from conflowgen.analyses.modal_split_analysis_report import ModalSplitAnalysisReport
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
        average_inbound_container_volume=300,
        vehicle_arrives_every_k_days=-1
    )
    schedule.save()
    feeder_lsv = LargeScheduledVehicle.create(
        vehicle_name="TestFeeder1",
        capacity_in_teu=300,
        inbound_container_volume=schedule.average_inbound_container_volume,
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


class TestModalSplitAnalysisReport(UnitTestCaseWithMatplotlib):
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
        self.analysis = ModalSplitAnalysisReport()

    def test_with_no_data(self):
        actual_report = self.analysis.get_report_as_text()
        expected_report = """
Role in network
transshipment traffic (in TEU):        0.00 (-%)
inland gateway traffic (in TEU):       0.00 (-%)

Modal split in hinterland traffic (only inbound traffic)
trucks (in TEU):        0.0 (-%)
barges (in TEU):        0.0 (-%)
trains (in TEU):        0.0 (-%)

Modal split in hinterland traffic (only outbound traffic)
trucks (in TEU):        0.0 (-%)
barges (in TEU):        0.0 (-%)
trains (in TEU):        0.0 (-%)

Modal split in hinterland traffic (both inbound and outbound traffic)
trucks (in TEU):        0.0 (-%)
barges (in TEU):        0.0 (-%)
trains (in TEU):        0.0 (-%)
(rounding errors might exist)
"""
        self.assertEqual(expected_report, actual_report)

    def test_inbound_with_single_feeder(self):
        setup_feeder_data()
        actual_report = self.analysis.get_report_as_text()
        expected_report = """
Role in network
transshipment traffic (in TEU):        0.00 (0.00%)
inland gateway traffic (in TEU):       1.00 (100.00%)

Modal split in hinterland traffic (only inbound traffic)
trucks (in TEU):        0.0 (-%)
barges (in TEU):        0.0 (-%)
trains (in TEU):        0.0 (-%)

Modal split in hinterland traffic (only outbound traffic)
trucks (in TEU):        1.0 (100.00%)
barges (in TEU):        0.0 (0.00%)
trains (in TEU):        0.0 (0.00%)

Modal split in hinterland traffic (both inbound and outbound traffic)
trucks (in TEU):        1.0 (100.00%)
barges (in TEU):        0.0 (0.00%)
trains (in TEU):        0.0 (0.00%)
(rounding errors might exist)
"""
        self.assertEqual(expected_report, actual_report)

    def test_graph_with_no_data(self):
        empty_graph = self.analysis.get_report_as_graph()
        self.assertIsNotNone(empty_graph)

    def test_graph_with_single_feeder(self):
        setup_feeder_data()
        graph = self.analysis.get_report_as_graph()
        self.assertIsNotNone(graph)

import datetime
import unittest

from conflowgen.application.models.container_flow_generation_properties import ContainerFlowGenerationProperties
from conflowgen.domain_models.arrival_information import TruckArrivalInformationForPickup, \
    TruckArrivalInformationForDelivery
from conflowgen.domain_models.container import Container
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.distribution_seeders import mode_of_transport_distribution_seeder
from conflowgen.domain_models.large_vehicle_schedule import Schedule, Destination
from conflowgen.domain_models.vehicle import LargeScheduledVehicle, Truck, Feeder, Train
from conflowgen.analyses.truck_gate_throughput_analysis_report import TruckGateThroughputAnalysisReport
from conflowgen.tests.autoclose_matplotlib import UnitTestWithMatplotlib
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


def setup_feeder_data():
    """When a feeder arrives, throughput at the quay side rises"""
    now = datetime.datetime.now()
    schedule = Schedule.create(
        vehicle_type=ModeOfTransport.feeder,
        service_name="TestFeederService",
        vehicle_arrives_at=now.date(),
        vehicle_arrives_at_time=now.time(),
        average_vehicle_capacity=300,
        average_moved_capacity=300,
    )
    feeder_lsv = LargeScheduledVehicle.create(
        vehicle_name="TestFeeder1",
        capacity_in_teu=300,
        moved_capacity=schedule.average_moved_capacity,
        scheduled_arrival=now,
        schedule=schedule
    )
    Feeder.create(
        large_scheduled_vehicle=feeder_lsv
    )
    aip = TruckArrivalInformationForPickup.create(
        realized_container_pickup_time=datetime.datetime.now() + datetime.timedelta(hours=25)
    )
    truck = Truck.create(
        delivers_container=False,
        picks_up_container=True,
        truck_arrival_information_for_delivery=None,
        truck_arrival_information_for_pickup=aip
    )
    Container.create(
        weight=20,
        length=ContainerLength.twenty_feet,
        storage_requirement=StorageRequirement.standard,
        delivered_by=ModeOfTransport.feeder,
        delivered_by_large_scheduled_vehicle=feeder_lsv,
        picked_up_by=ModeOfTransport.truck,
        picked_up_by_initial=ModeOfTransport.truck,
        picked_up_by_truck=truck
    )
    aip_2 = TruckArrivalInformationForPickup.create(
        realized_container_pickup_time=datetime.datetime.now() + datetime.timedelta(hours=12)
    )
    truck_2 = Truck.create(
        delivers_container=False,
        picks_up_container=True,
        truck_arrival_information_for_delivery=None,
        truck_arrival_information_for_pickup=aip_2
    )
    Container.create(
        weight=20,
        length=ContainerLength.forty_feet,
        storage_requirement=StorageRequirement.standard,
        delivered_by=ModeOfTransport.feeder,
        delivered_by_large_scheduled_vehicle=feeder_lsv,
        picked_up_by=ModeOfTransport.truck,
        picked_up_by_initial=ModeOfTransport.truck,
        picked_up_by_truck=truck_2
    )


class TestTruckGateThroughputAnalysisReport(unittest.TestCase, UnitTestWithMatplotlib):
    def setUp(self) -> None:
        """Create container database in memory"""
        self.sqlite_db = setup_sqlite_in_memory_db()
        self.sqlite_db.create_tables([
            Schedule,
            Container,
            LargeScheduledVehicle,
            Truck,
            TruckArrivalInformationForPickup,
            TruckArrivalInformationForDelivery,
            Feeder,
            ModeOfTransportDistribution,
            Destination,
            ContainerFlowGenerationProperties,
            Train
        ])
        mode_of_transport_distribution_seeder.seed()
        ContainerFlowGenerationProperties.create(
            start_date=datetime.datetime(2021, 12, 1),
            end_date=datetime.datetime(2021, 12, 6)
        )
        self.analysis = TruckGateThroughputAnalysisReport()

    def test_with_no_data(self):
        """If no schedules are provided, no throughput is generated"""
        actual_report = self.analysis.get_report_as_text()
        expected_report = """
                                     (reported in boxes)
maximum hourly truck gate throughput:                  0
average hourly truck gate throughput:                0.0
standard deviation:                                 -1.0
(rounding errors might exist)
"""
        self.assertEqual(actual_report, expected_report)

    def test_with_two_trucks(self):
        setup_feeder_data()
        actual_report = self.analysis.get_report_as_text()
        expected_report = """
                                     (reported in boxes)
maximum hourly truck gate throughput:                  1
average hourly truck gate throughput:                0.1
standard deviation:                                  0.3
(rounding errors might exist)
"""
        self.assertEqual(actual_report, expected_report)

    def test_with_train(self):
        """The train is ignored during reporting"""
        now = datetime.datetime.now()
        schedule = Schedule.create(
            vehicle_type=ModeOfTransport.train,
            service_name="TestTrainService",
            vehicle_arrives_at=now.date(),
            vehicle_arrives_at_time=now.time(),
            average_vehicle_capacity=90,
            average_moved_capacity=90,
        )
        train_lsv = LargeScheduledVehicle.create(
            vehicle_name="TestTrain1",
            capacity_in_teu=90,
            moved_capacity=schedule.average_moved_capacity,
            scheduled_arrival=now,
            schedule=schedule
        )
        Train.create(
            large_scheduled_vehicle=train_lsv
        )
        aip = TruckArrivalInformationForPickup.create(
            realized_container_pickup_time=datetime.datetime.now() + datetime.timedelta(hours=25)
        )
        Truck.create(
            delivers_container=False,
            picks_up_container=True,
            truck_arrival_information_for_delivery=None,
            truck_arrival_information_for_pickup=aip
        )
        Container.create(
            weight=20,
            length=ContainerLength.twenty_feet,
            storage_requirement=StorageRequirement.standard,
            delivered_by=ModeOfTransport.train,
            delivered_by_large_scheduled_vehicle=train_lsv,
            picked_up_by=ModeOfTransport.train,
            picked_up_by_initial=ModeOfTransport.truck,
            picked_up_by_large_scheduled_vehicle=train_lsv
        )
        actual_report = self.analysis.get_report_as_text()
        expected_report = """
                                     (reported in boxes)
maximum hourly truck gate throughput:                  0
average hourly truck gate throughput:                0.0
standard deviation:                                 -1.0
(rounding errors might exist)
"""
        self.assertEqual(actual_report, expected_report)

    def test_graph_with_no_data(self):
        empty_graph = self.analysis.get_report_as_graph()
        self.assertIsNotNone(empty_graph)

    def test_graph_with_two_trucks(self):
        setup_feeder_data()
        graph = self.analysis.get_report_as_graph()
        self.assertIsNotNone(graph)

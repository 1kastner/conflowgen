import datetime
import unittest

from conflowgen.analyses.truck_gate_throughput_analysis import TruckGateThroughputAnalysis
from conflowgen.domain_models.arrival_information import TruckArrivalInformationForPickup, \
    TruckArrivalInformationForDelivery
from conflowgen.domain_models.container import Container
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.distribution_seeders import mode_of_transport_distribution_seeder
from conflowgen.domain_models.large_vehicle_schedule import Schedule, Destination
from conflowgen.domain_models.vehicle import LargeScheduledVehicle, Truck, Feeder
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestTruckGateThroughputAnalysis(unittest.TestCase):
    def setUp(self) -> None:
        """Create container database in memory"""
        self.sqlite_db = setup_sqlite_in_memory_db()
        self.sqlite_db.create_tables([
            Schedule,
            Container,
            LargeScheduledVehicle,
            Truck,
            TruckArrivalInformationForDelivery,
            TruckArrivalInformationForPickup,
            Feeder,
            ModeOfTransportDistribution,
            Destination
        ])
        mode_of_transport_distribution_seeder.seed()
        self.analysis = TruckGateThroughputAnalysis()

    def test_with_no_data(self):
        """If no schedules are provided, no capacity is needed"""
        no_action_at_truck_gate = self.analysis.get_throughput_over_time()
        self.assertEqual(no_action_at_truck_gate, {})

    def test_with_single_container(self):
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

        truck_gate_throughput = self.analysis.get_throughput_over_time()
        self.assertEqual(3, len(truck_gate_throughput))
        self.assertSetEqual({0, 1}, set(truck_gate_throughput.values()))

    def test_with_two_containers(self):
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

        truck_gate_throughput = self.analysis.get_throughput_over_time()
        self.assertEqual(16, len(truck_gate_throughput))
        self.assertSetEqual({0, 1}, set(truck_gate_throughput.values()))

    def test_with_two_containers_and_end_time(self):
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

        truck_gate_throughput = self.analysis.get_throughput_over_time(
            start_date=now,
            end_date=now + datetime.timedelta(hours=14)
        )
        self.assertEqual(17, len(truck_gate_throughput))
        self.assertSetEqual({0, 1}, set(truck_gate_throughput.values()))

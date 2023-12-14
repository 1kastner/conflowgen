import datetime
import unittest

from conflowgen.analyses.yard_capacity_analysis import YardCapacityAnalysis
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


class TestYardCapacityAnalysis(unittest.TestCase):
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
        self.analysis = YardCapacityAnalysis(
            transportation_buffer=0.2
        )

    def test_with_no_data(self):
        """If no schedules are provided, no capacity is needed"""
        empty_yard = self.analysis.get_used_yard_capacity_over_time().teu
        self.assertEqual(empty_yard, {})

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

        used_yard_over_time = self.analysis.get_used_yard_capacity_over_time(smoothen_peaks=False).teu
        self.assertEqual(len(used_yard_over_time), 28)
        self.assertSetEqual(set(used_yard_over_time.values()), {0, 1})

        used_yard_over_time = self.analysis.get_used_yard_capacity_over_time(smoothen_peaks=True).teu
        self.assertEqual(len(used_yard_over_time), 27)
        self.assertSetEqual(set(used_yard_over_time.values()), {0, 1})

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

        used_yard_over_time = self.analysis.get_used_yard_capacity_over_time(smoothen_peaks=False).teu
        self.assertEqual(len(used_yard_over_time), 28)
        self.assertSetEqual(set(used_yard_over_time.values()), {0, 1, 3})

        used_yard_over_time = self.analysis.get_used_yard_capacity_over_time(smoothen_peaks=True).teu
        self.assertEqual(len(used_yard_over_time), 27)
        self.assertSetEqual(set(used_yard_over_time.values()), {0, 1, 3})

    def test_with_container_group(self):
        now = datetime.datetime.now()
        schedule = Schedule.create(
            vehicle_type=ModeOfTransport.feeder,
            service_name="TestFeederService",
            vehicle_arrives_at=now.date(),
            vehicle_arrives_at_time=now.time(),
            average_vehicle_capacity=300,
            average_moved_capacity=300,
        )
        feeder_lsv_1 = LargeScheduledVehicle.create(
            vehicle_name="TestFeeder1",
            capacity_in_teu=300,
            moved_capacity=schedule.average_moved_capacity,
            scheduled_arrival=now,
            schedule=schedule
        )
        Feeder.create(
            large_scheduled_vehicle=feeder_lsv_1
        )
        feeder_lsv_2 = LargeScheduledVehicle.create(
            vehicle_name="TestFeeder2",
            capacity_in_teu=300,
            moved_capacity=schedule.average_moved_capacity,
            scheduled_arrival=now + datetime.timedelta(hours=72),
            schedule=schedule
        )
        for _ in range(20):
            Container.create(
                weight=20,
                length=ContainerLength.twenty_feet,
                storage_requirement=StorageRequirement.standard,
                delivered_by=ModeOfTransport.feeder,
                delivered_by_large_scheduled_vehicle=feeder_lsv_1,
                picked_up_by=ModeOfTransport.truck,
                picked_up_by_initial=ModeOfTransport.truck,
                picked_up_by_large_scheduled_vehicle=feeder_lsv_2
            )

        used_yard_over_time = self.analysis.get_used_yard_capacity_over_time(smoothen_peaks=False).teu
        self.assertEqual(len(used_yard_over_time), 75)
        self.assertSetEqual(set(used_yard_over_time.values()), {0, 20})
        self.assertIn(now.replace(minute=0, second=0, microsecond=0), set(used_yard_over_time.keys()))
        self.assertListEqual(list(used_yard_over_time.values()), [0] + [20] * 73 + [0])

        used_yard_over_time = self.analysis.get_used_yard_capacity_over_time(smoothen_peaks=True).teu
        self.assertEqual(len(used_yard_over_time), 74)
        self.assertSetEqual(set(used_yard_over_time.values()), {0, 20})
        self.assertIn(now.replace(minute=0, second=0, microsecond=0), set(used_yard_over_time.keys()))
        self.assertListEqual(list(used_yard_over_time.values()), [0] + [20] * 72 + [0])

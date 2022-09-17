import datetime
import unittest

from conflowgen import VehicleIdentifier
from conflowgen.analyses.container_flow_vehicle_type_adjustment_per_vehicle_analysis import \
    ContainerFlowVehicleTypeAdjustmentPerVehicleAnalysis
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


class TestContainerFlowVehicleTypeAdjustmentPerVehicleAnalysis(unittest.TestCase):
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
            TruckArrivalInformationForPickup,
            TruckArrivalInformationForDelivery
        ])
        mode_of_transport_distribution_seeder.seed()
        self.analysis = ContainerFlowVehicleTypeAdjustmentPerVehicleAnalysis()

    def test_with_no_data(self):
        """If no schedules are provided, no capacity is needed"""
        empty_result = self.analysis.get_vehicle_type_adjustments_per_vehicle()
        self.assertDictEqual(empty_result, {})

    def test_with_feeder_and_truck_and_no_adjustment(self):
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
        inbound_feeder_lsv = LargeScheduledVehicle.create(
            vehicle_name="TestFeeder1",
            capacity_in_teu=300,
            moved_capacity=schedule.average_moved_capacity,
            scheduled_arrival=datetime.datetime.now(),
            schedule=schedule
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

        no_adjustment = self.analysis.get_vehicle_type_adjustments_per_vehicle()
        self.assertListEqual(list(no_adjustment.values()), [0])
        vehicle_identifier = list(no_adjustment.keys())[0]
        self.assertEqual(vehicle_identifier, VehicleIdentifier(
            mode_of_transport=ModeOfTransport.feeder,
            vehicle_arrival_time=vessel_arrival,
            service_name="TestFeederService",
            vehicle_name="TestFeeder2"
        ))

    def test_with_feeder_and_truck_and_one_adjusted_box(self):
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
        feeder_lsv = LargeScheduledVehicle.create(
            vehicle_name="TestFeeder1",
            capacity_in_teu=300,
            moved_capacity=schedule.average_moved_capacity,
            scheduled_arrival=datetime.datetime.now(),
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
            delivered_by=ModeOfTransport.truck,
            delivered_by_truck=truck,
            picked_up_by=ModeOfTransport.feeder,
            picked_up_by_initial=ModeOfTransport.deep_sea_vessel,
            picked_up_by_large_scheduled_vehicle=feeder_lsv
        )

        no_adjustment = self.analysis.get_vehicle_type_adjustments_per_vehicle()
        self.assertListEqual(list(no_adjustment.values()), [1])

    def test_with_feeder_and_truck_and_some_adjustments(self):
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
        feeder_lsv = LargeScheduledVehicle.create(
            vehicle_name="TestFeeder1",
            capacity_in_teu=300,
            moved_capacity=schedule.average_moved_capacity,
            scheduled_arrival=datetime.datetime.now(),
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
            delivered_by=ModeOfTransport.truck,
            delivered_by_truck=truck,
            picked_up_by=ModeOfTransport.feeder,
            picked_up_by_initial=ModeOfTransport.deep_sea_vessel,
            picked_up_by_large_scheduled_vehicle=feeder_lsv
        )
        Container.create(
            weight=20,
            length=ContainerLength.twenty_feet,
            storage_requirement=StorageRequirement.standard,
            delivered_by=ModeOfTransport.truck,
            delivered_by_truck=truck,
            picked_up_by=ModeOfTransport.feeder,
            picked_up_by_initial=ModeOfTransport.feeder,
            picked_up_by_large_scheduled_vehicle=feeder_lsv
        )

        half_half = self.analysis.get_vehicle_type_adjustments_per_vehicle()
        self.assertListEqual(list(half_half.values()), [0.5])

    def test_with_truck_and_feeder_and_no_adjustment(self):
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
        feeder_arrival = datetime.datetime.now()
        feeder_lsv = LargeScheduledVehicle.create(
            vehicle_name="TestFeeder1",
            capacity_in_teu=300,
            moved_capacity=schedule.average_moved_capacity,
            scheduled_arrival=feeder_arrival,
            schedule=schedule
        )
        Feeder.create(
            large_scheduled_vehicle=feeder_lsv
        )
        truck_delivery = datetime.datetime.now() - datetime.timedelta(hours=25)
        aid = TruckArrivalInformationForDelivery.create(
            realized_container_delivery_time=truck_delivery
        )
        truck = Truck.create(
            delivers_container=False,
            picks_up_container=True,
            truck_arrival_information_for_delivery=aid,
            truck_arrival_information_for_pickup=None
        )
        Container.create(
            weight=20,
            length=ContainerLength.twenty_feet,
            storage_requirement=StorageRequirement.standard,
            delivered_by=ModeOfTransport.truck,
            delivery_by_truck=truck,
            picked_up_by=ModeOfTransport.feeder,
            picked_up_by_initial=ModeOfTransport.feeder,
            picked_up_by_large_scheduled_vehicle=feeder_lsv
        )

        no_adjustment = self.analysis.get_vehicle_type_adjustments_per_vehicle()
        self.assertListEqual(list(no_adjustment.values()), [0])
        vehicle_identifier = list(no_adjustment.keys())[0]

        self.assertEqual(vehicle_identifier, VehicleIdentifier(
            mode_of_transport=ModeOfTransport.feeder,
            vehicle_arrival_time=feeder_arrival,
            service_name="TestFeederService",
            vehicle_name="TestFeeder1"
        ))

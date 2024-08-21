import datetime
import unittest

from conflowgen.analyses.modal_split_analysis import ModalSplitAnalysis
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


class TestModalSplitAnalysis(unittest.TestCase):
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
        self.analysis = ModalSplitAnalysis()

    def test_transshipment_share_with_no_data(self):
        both_zero = self.analysis.get_transshipment_and_hinterland_split()
        self.assertSetEqual(set(both_zero), {0})

    def test_hinterland_split_with_no_data(self):
        all_three_zero = self.analysis.get_modal_split_for_hinterland_traffic(True, True)
        self.assertSetEqual(set(all_three_zero), {0})

    def test_transshipment_share_with_single_feeder(self):
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
        feeder_lsv = LargeScheduledVehicle.create(
            vehicle_name="TestFeeder1",
            capacity_in_teu=300,
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
            delivered_by=ModeOfTransport.feeder,
            delivered_by_large_scheduled_vehicle=feeder_lsv,
            picked_up_by=ModeOfTransport.truck,
            picked_up_by_initial=ModeOfTransport.truck
        )

        fractions = self.analysis.get_transshipment_and_hinterland_split()
        self.assertEqual(fractions.transshipment_capacity, 0)
        self.assertEqual(fractions.hinterland_capacity, 1)

    def test_outbound_with_single_feeder(self):
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
        feeder_lsv = LargeScheduledVehicle.create(
            vehicle_name="TestFeeder1",
            capacity_in_teu=300,
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
            delivered_by=ModeOfTransport.feeder,
            delivered_by_large_scheduled_vehicle=feeder_lsv,
            picked_up_by=ModeOfTransport.truck,
            picked_up_by_initial=ModeOfTransport.truck
        )

        fractions = self.analysis.get_modal_split_for_hinterland_traffic(True, True)
        self.assertEqual(fractions.truck_capacity, 1)
        self.assertEqual(fractions.barge_capacity, 0)
        self.assertEqual(fractions.train_capacity, 0)

    def test_outbound_with_single_feeder_and_not_affecting_start_and_end(self):
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
        feeder_lsv = LargeScheduledVehicle.create(
            vehicle_name="TestFeeder1",
            capacity_in_teu=300,
            inbound_container_volume=schedule.average_inbound_container_volume,
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
            delivered_by=ModeOfTransport.feeder,
            delivered_by_large_scheduled_vehicle=feeder_lsv,
            picked_up_by=ModeOfTransport.truck,
            picked_up_by_truck=truck,
            picked_up_by_initial=ModeOfTransport.truck
        )

        long_time = datetime.timedelta(hours=9999)

        fractions = self.analysis.get_modal_split_for_hinterland_traffic(
            True, True, one_week_later - long_time, one_week_later + long_time
        )
        self.assertEqual(fractions.truck_capacity, 1)
        self.assertEqual(fractions.barge_capacity, 0)
        self.assertEqual(fractions.train_capacity, 0)

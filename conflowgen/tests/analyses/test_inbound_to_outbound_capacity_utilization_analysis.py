import datetime
import unittest

from conflowgen.descriptive_datatypes import VehicleIdentifier
from conflowgen.analyses.outbound_to_inbound_vehicle_capacity_utilization_analysis import \
    OutboundToInboundVehicleCapacityUtilizationAnalysis
from conflowgen.domain_models.container import Container
from conflowgen.domain_models.data_types.container_length import ContainerLength
from conflowgen.domain_models.data_types.mode_of_transport import ModeOfTransport
from conflowgen.domain_models.data_types.storage_requirement import StorageRequirement
from conflowgen.domain_models.distribution_models.mode_of_transport_distribution import ModeOfTransportDistribution
from conflowgen.domain_models.distribution_seeders import mode_of_transport_distribution_seeder
from conflowgen.domain_models.large_vehicle_schedule import Schedule, Destination
from conflowgen.domain_models.vehicle import LargeScheduledVehicle, Truck, Feeder
from conflowgen.tests.substitute_peewee_database import setup_sqlite_in_memory_db


class TestInboundToOutboundCapacityUtilizationAnalysis(unittest.TestCase):
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
            Destination
        ])
        mode_of_transport_distribution_seeder.seed()
        self.analysis = OutboundToInboundVehicleCapacityUtilizationAnalysis(
            transportation_buffer=0.2
        )

    def test_with_no_data(self):
        """If no schedules are provided, no capacity is needed"""
        empty_capacities = self.analysis.get_inbound_and_outbound_capacity_of_each_vehicle()
        self.assertDictEqual({}, empty_capacities)

    def test_with_no_data_and_start_and_end_date(self):
        empty_capacities = self.analysis.get_inbound_and_outbound_capacity_of_each_vehicle(
            start_date=datetime.datetime(2022, 9, 15),
            end_date=datetime.datetime(2022, 9, 16)
        )
        self.assertDictEqual({}, empty_capacities)

    def test_inbound_with_single_feeder(self):
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
        now = datetime.datetime.now()
        feeder_lsv = LargeScheduledVehicle.create(
            vehicle_name="TestFeeder1",
            capacity_in_teu=schedule.average_vehicle_capacity,
            inbound_container_volume=schedule.average_inbound_container_volume,
            scheduled_arrival=now,
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

        capacities_with_one_feeder = self.analysis.get_inbound_and_outbound_capacity_of_each_vehicle()

        self.assertEqual(len(capacities_with_one_feeder), 1, "There is only one vehicle")

        key_of_entry: VehicleIdentifier = list(capacities_with_one_feeder.keys())[0]
        self.assertEqual(len(key_of_entry), 5, "Key consists of five components")
        self.assertEqual(key_of_entry.mode_of_transport, ModeOfTransport.feeder)
        self.assertEqual(key_of_entry.service_name, "TestFeederService")
        self.assertEqual(key_of_entry.vehicle_name, "TestFeeder1")
        self.assertEqual(key_of_entry.vehicle_arrival_time, now)

        value_of_entry = list(capacities_with_one_feeder.values())[0]
        self.assertEqual(len(value_of_entry), 2, "Value consists of two components")
        (used_capacity_on_inbound_journey, used_capacity_on_outbound_journey) = value_of_entry
        self.assertEqual(used_capacity_on_inbound_journey, 250)
        self.assertEqual(used_capacity_on_outbound_journey, 1, "One 20' is loaded")
